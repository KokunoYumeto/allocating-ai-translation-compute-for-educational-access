"""Deterministic, self-contained build for the bounded Telugu A10 m82630 packet."""

from pathlib import Path
from lxml import etree as E
from lxml import html as LH
from urllib.parse import urlparse
import hashlib
import html
import json
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source/m82630.en.cnxml"
COLLECTION = ROOT / "source/collection.xml"
SOURCE_SHA = "d9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b"
COLLECTION_SHA = "5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72"
LICENSE_SHA = "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
CANONICAL_SOURCE_URL = (
    "https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/"
    f"{COMMIT}/modules/m82630/index.cnxml"
)
BOOK_URL = "https://openstax.org/details/books/elementary-algebra-2e"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
TS_WITNESS_URL = "https://scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf"
NS = {"c": "http://cnx.rice.edu/cnxml", "md": "http://cnx.rice.edu/mdml"}
COL_NS = {"col": "http://cnx.rice.edu/collxml"}
ASSET_LOCKS = {
    "CNX_ElemAlg_Figure_05_01_015_img.jpg": (
        688493,
        "34fd0299880bc134f6308adcb2296ec1e145431909a1ab1cc2b507e01e3670f4",
    ),
    "howtoicon.png": (
        1681,
        "67f2344cdbe25b192fbdee0d904ce912e4e15aed5bf0063f61a192dd0b0b5826",
    ),
    "media.png": (
        353,
        "140b45d7d047dc59b236c95bb2c2a237ca5b748b290b28f8e6d9f8f520077e6a",
    ),
    "tryit.png": (
        344,
        "7f9c8c226d8b937d4070c69326d6c2ac7df37a74c85fa8cec64e2ad7bef59ebf",
    ),
}
EXCLUDED_FROM_PAYLOAD = {
    "CHECKSUMS.sha256",
    "MANIFEST.json",
    "PACKAGE.json",
    "PACKAGE.zip",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def slots(document):
    result = []
    for element in document.iter():
        local = E.QName(element).localname
        if local in ("content-id", "uuid", "abstract"):
            continue
        if element.text and element.text.strip():
            result.append((element, "text", element.text))
        if element.tail and element.tail.strip():
            result.append((element, "tail", element.tail))
        if element.get("alt"):
            result.append((element, "alt", element.get("alt")))
    return result


source_bytes = SOURCE.read_bytes()
assert sha(source_bytes) == SOURCE_SHA
collection_bytes = COLLECTION.read_bytes()
assert sha(collection_bytes) == COLLECTION_SHA
assert sha((ROOT / "LICENSE.txt").read_bytes()) == LICENSE_SHA

source_doc = E.fromstring(source_bytes)
source_slots = slots(source_doc)
if "--list" in sys.argv:
    for n, (element, field, source_text) in enumerate(source_slots):
        print(
            json.dumps(
                {
                    "n": n,
                    "tag": E.QName(element).localname,
                    "field": field,
                    "id": element.get("id"),
                    "en": source_text,
                },
                ensure_ascii=False,
            )
        )
    raise SystemExit

collection_doc = E.fromstring(collection_bytes)
collection_modules = collection_doc.xpath("//col:module/@document", namespaces=COL_NS)
assert len(collection_modules) == 82
assert collection_modules[:2] == ["m82630", "m82451"]
assert len(collection_modules) == len(set(collection_modules))

recovery = read_json(ROOT / "SOURCE_RECOVERY.json")
assert recovery["locale"] == "te-Telu-IN" and recovery["module"] == "m82630"
assert recovery["canonical_commit"] == COMMIT
assert recovery["canonical_module_sha256"] == SOURCE_SHA
assert recovery["canonical_source_url"] == CANONICAL_SOURCE_URL
assert recovery["baseline_A10_crosswalk"] == {
    "modules": 82,
    "statuses": {"not_started": 82},
}
assert recovery["next_module"]["source_id"] == "m82451"
assert recovery["next_module"]["source_sha256"] == (
    "025f994e3c66f19462c9423788f703f7987fecb67656911d840fdd15a58d8a4a"
)

mapping = read_json(ROOT / "translation.json")
assert mapping["source_sha256"] == SOURCE_SHA
translated_keys = set(map(int, mapping["translations"]))
retained_keys = set(mapping["retain_source_slots"])
assert translated_keys | retained_keys == set(range(len(source_slots)))
assert not translated_keys & retained_keys
assert all(
    re.search("[\u0c00-\u0c7f]", value)
    for value in mapping["translations"].values()
)

doc = E.fromstring(source_bytes)
doc_slots = slots(doc)
source_tree = E.ElementTree(E.fromstring(source_bytes))
source_elements = list(source_tree.getroot().iter())
doc_elements = list(doc.iter())
segments = []
for n, (element, field, source_text) in enumerate(doc_slots):
    target_text = mapping["translations"].get(str(n), source_text)
    source_element = source_elements[doc_elements.index(element)]
    segments.append(
        {
            "unit": "m82630",
            "slot": n,
            "xpath": source_tree.getpath(source_element),
            "field": field,
            "source": source_text,
            "target": target_text,
            "status": "credit-retained" if n in retained_keys else "translated",
            "source_text_sha256": sha(source_text.encode("utf-8")),
            "target_text_sha256": sha(target_text.encode("utf-8")),
        }
    )
    if field == "alt":
        element.set("alt", target_text)
    else:
        setattr(element, field, target_text)
doc.set("{http://www.w3.org/XML/1998/namespace}lang", "te")

(ROOT / "translated/modules/m82630").mkdir(parents=True, exist_ok=True)
(ROOT / "translated/media").mkdir(parents=True, exist_ok=True)
translated_bytes = E.tostring(
    doc, encoding="UTF-8", xml_declaration=True, pretty_print=False
)
(ROOT / "translated/modules/m82630/index.cnxml").write_bytes(translated_bytes)
write_json(
    ROOT / "SEGMENTS.json",
    {
        "schema": "source-id-text-slots-v1",
        "locale": "te-Telu-IN",
        "module": "m82630",
        "segments": segments,
    },
)

asset_records = []
source_asset_names = []
for image_element in doc.findall(".//c:image", NS):
    name = Path(image_element.get("src")).name
    source_asset_names.append(name)
    assert name in ASSET_LOCKS
    local_path = ROOT / "translated/media" / name
    asset_bytes = local_path.read_bytes()
    expected_bytes, expected_sha = ASSET_LOCKS[name]
    assert len(asset_bytes) == expected_bytes and sha(asset_bytes) == expected_sha
    asset_records.append(
        {
            "path": f"translated/media/{name}",
            "source_reference": image_element.get("src"),
            "canonical_asset_url": (
                "https://raw.githubusercontent.com/openstax/"
                f"osbooks-prealgebra-bundle/{COMMIT}/media/{name}"
            ),
            "bytes": len(asset_bytes),
            "sha256": sha(asset_bytes),
            "treatment": (
                "Original raster bytes unchanged. Telugu alt text is in the translated "
                "CNXML; the English graph also has a visible Telugu description."
            ),
        }
    )
assert sorted(source_asset_names) == sorted(ASSET_LOCKS)

source_ids = E.fromstring(source_bytes).xpath("//@id")
source_and_credits = {
    "schema": "a10.packet-source-and-credits.v1",
    "locale": "te-Telu-IN",
    "packet_scope": "OpenStax Elementary Algebra 2e preface module m82630 only",
    "full_a10_status": "partial: 1 of 82 ordered modules complete",
    "canonical": {
        "collection_id": "col31130",
        "commit": COMMIT,
        "module_id": "m82630",
        "module_title": "Preface",
        "module_url": CANONICAL_SOURCE_URL,
        "book_url": BOOK_URL,
        "source_sha256": SOURCE_SHA,
        "collection_sha256": COLLECTION_SHA,
        "ordered_collection_modules": len(collection_modules),
        "source_ids": source_ids,
        "source_id_count": len(source_ids),
        "mathml_elements": int(
            E.fromstring(source_bytes).xpath("count(//*[local-name()='math'])")
        ),
    },
    "assets": sorted(asset_records, key=lambda record: record["path"]),
    "licence": {
        "name": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        "identifier": "CC BY-NC-SA 4.0",
        "url": LICENSE_URL,
        "local_notice": "LICENSE.txt",
        "local_notice_sha256": LICENSE_SHA,
        "qualification": "Subject to component-specific restrictions and credits.",
    },
    "original_credits": {
        "copyright": "Rice University, OpenStax",
        "authors": [
            "Lynn Marecek",
            "MaryAnne Anthony-Smith",
            "Andrea Honeycutt Mathis",
        ],
        "additional_contributors": (
            "All reviewer names and institutional affiliations are retained in source order "
            "in translated/modules/m82630/index.cnxml."
        ),
        "trademark_notice": (
            "OpenStax and Rice University do not endorse this translation; their marks are "
            "not licensed."
        ),
    },
    "translation_credit": "OpenAI Codex gpt-5.6-sol, Ultra",
    "regional_terminology_witness": {
        "id": "TS6-2018",
        "url": TS_WITNESS_URL,
        "sha256": "3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee",
        "use": (
            "Terminology evidence only; no Telangana textbook page, OCR, or raster is "
            "redistributed. Andhra Pradesh evidence remains not acquired."
        ),
    },
}
write_json(ROOT / "SOURCE_AND_CREDITS.json", source_and_credits)

expert_log = read_json(ROOT / "EXPERT_REVIEW_LOG.json")
required_entry_fields = {
    "decision_id",
    "source_location",
    "target_location",
    "source_sense",
    "chosen_wording",
    "authorities_checked",
    "rationale",
    "alternatives",
    "uncertainty",
    "provisional",
    "review_question",
    "rationale_timing",
}
assert expert_log["schema"] == "a10.expert-review-log.v1"
assert expert_log["locale"] == "te-Telu-IN"
assert expert_log["coverage_status"] == "complete"
assert expert_log["packet_scope"] == "m82630"
decision_ids = []
covered_terms = set()
for entry in expert_log["entries"]:
    assert required_entry_fields <= set(entry)
    assert entry["authorities_checked"]
    assert entry["rationale_timing"] in {
        "contemporaneous",
        "retrospective_reconstruction",
    }
    assert entry["review_question"].strip()
    decision_ids.append(entry["decision_id"])
    covered_terms.update(entry.get("terms_covered", []))
assert len(decision_ids) == len(set(decision_ids))

terminology = read_json(ROOT / "TERMINOLOGY.json")
terms = terminology["terms"]
assert {term["en"] for term in terms} == covered_terms


def esc(value):
    return html.escape(value or "", quote=True)


english_credit_para_ids = {
    "eip-855",
    "eip-250",
    "eip-478",
    "eip-id1169146105286",
}


def render(element):
    tag = E.QName(element).localname
    ident = f' id="{esc(element.get("id"))}"' if element.get("id") else ""
    body = esc(element.text)
    for child in element:
        body += render(child) + esc(child.tail)
    if tag == "content":
        return body
    if tag == "section":
        return f"<section{ident}>{body}</section>"
    if tag == "title":
        level = min(
            6,
            1
            + sum(
                E.QName(ancestor).localname == "section"
                for ancestor in element.iterancestors()
            ),
        )
        return f"<h{level}>{body}</h{level}>"
    if tag == "para":
        credit = (
            ' class="english-credit" lang="en"'
            if element.get("id") in english_credit_para_ids
            else ""
        )
        return f"<p{ident}{credit}>{body}</p>"
    if tag == "emphasis":
        markup = "strong" if element.get("effect") == "bold" else "em"
        return f"<{markup}>{body}</{markup}>"
    if tag == "list":
        list_class = ' class="plain"' if element.get("bullet-style") == "none" else ""
        return f"<ul{ident}{list_class}>{body}</ul>"
    if tag == "item":
        return f"<li{ident}>{body}</li>"
    if tag == "newline":
        return "<br>"
    if tag == "media":
        image_element = element.find("c:image", NS)
        assert image_element is not None
        image_markup = (
            '<img src="translated/media/'
            + esc(Path(image_element.get("src")).name)
            + '" alt="'
            + esc(element.get("alt"))
            + '">'
        )
        if E.QName(element.getparent()).localname == "para":
            return f'<span class="icon"{ident}>{image_markup}</span>'
        return (
            f'<figure class="art"{ident}>{image_markup}'
            "<figcaption>మూల చిత్రంలోని అక్షరాలు ఆంగ్లంలోనే ఉన్నాయి. దాని పూర్తి తెలుగు "
            f"వివరణ: {esc(element.get('alt'))}</figcaption></figure>"
        )
    if tag == "image":
        return ""
    raise ValueError(f"Unrendered CNXML element: {tag}")


content = doc.find("c:content", NS)
toc = "".join(
    '<li><a href="#'
    + esc(section.get("id"))
    + '">'
    + esc("".join(section.find("c:title", NS).itertext()))
    + "</a></li>"
    for section in content.findall("c:section", NS)
)
bridge = (
    '<section id="te-english-bridge" class="support">'
    '<p class="eyebrow">అనువాదానికి విడిగా జోడించిన English-term bridge</p>'
    "<h2>తెలుగు పదాలు — ఆంగ్ల పదాలు</h2>"
    "<p>ముందుమాటలోని తెలుగు గణిత పదాలను ఆంగ్ల వనరులతో అనుసంధానించడానికి ఈ జాబితా "
    "ఉపయోగపడుతుంది. <span lang=\"en\">whole numbers</span>, <span lang=\"en\">integers</span> "
    "అనే పదాల భేదాన్ని తెలంగాణ పాఠ్యపుస్తకంతో సరిచూశాం. ఇతర ఉన్నత బీజగణిత పదాలు ఈ "
    "ముందుమాట కోసం చేసిన తాత్కాలిక సంపాదకీయ ఎంపికలు; అవి ఆంధ్రప్రదేశ్ లేదా తెలంగాణ "
    "అధికారిక పదజాలమని ధ్రువీకరించడం లేదు.</p><div class=\"bridge-list\">"
)
for term in terms:
    bridge += (
        '<div class="term"><strong>'
        + esc(term["te"])
        + '</strong><span lang="en">'
        + esc(term["en"])
        + "</span>"
    )
    if term.get("meaning_te"):
        bridge += "<small>" + esc(term["meaning_te"]) + "</small>"
    bridge += "</div>"
bridge += "</div></section>"

support_document = LH.parse(str(ROOT / "learning-support.html"))
support_sections = support_document.xpath('//section[@id="te-learning-support"]')
assert len(support_sections) == 1
support_fragment = LH.tostring(
    support_sections[0], encoding="unicode", method="html", with_tail=False
)

page = (
    '<!doctype html><html lang="te"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    '<meta name="description" content="OpenStax Elementary Algebra 2e ముందుమాట — తెలుగు అనువాదం">'
    "<title>ముందుమాట | ప్రాథమిక బీజగణితం 2e | తెలుగు</title>"
    '<link rel="icon" href="translated/media/media.png">'
    '<link rel="stylesheet" href="style.css"></head><body>'
    '<a class="skip" href="#source-preface">పాఠ్యానికి వెళ్లండి</a><header>'
    '<p class="eyebrow">OPENSTAX • ELEMENTARY ALGEBRA 2e • te-Telu-IN • m82630</p>'
    "<h1>ముందుమాట</h1><p>ప్రాథమిక బీజగణితం, రెండవ సంచిక</p>"
    '<p class="status">ఈ ముందుమాట పూర్తి అనువాదం. మొత్తం పుస్తక అనువాదం ఇంకా అసంపూర్ణం. '
    "ఈ ప్యాకెట్ మూల మాడ్యూల్ <span lang=\"en\">m82630</span>ను మాత్రమే కలిగి ఉంది; "
    "తరువాతి మూల మాడ్యూల్ <span lang=\"en\">m82451</span>.</p>"
    '<nav aria-label="ఈ పేజీలోని భాగాలు"><ul>'
    + toc
    + '<li><a href="#te-english-bridge">తెలుగు — ఆంగ్ల పదాలు</a></li>'
    '<li><a href="#te-learning-support">పఠన సహాయం, స్వీయ పరిశీలన</a></li>'
    '<li><a href="#edition-notes">మూలం, సంచిక గమనికలు</a></li></ul></nav></header>'
    '<main><article id="source-preface" aria-label="మూల ముందుమాట పూర్తి తెలుగు అనువాదం">'
    + render(content)
    + "</article>"
    + bridge
    + support_fragment
    + '<section id="edition-notes" class="source-notes"><h2>మూలం, సంచిక గమనికలు</h2>'
    "<p>పై ముందుమాట మూల పాఠ్యపు అనువాదం. పదాల జాబితా, పఠన సహాయం విడిగా జోడించినవి. "
    "మూలం ‘మాధ్యమ వనరులు’ గమనికలో <span lang=\"en\"><em>Prealgebra 2e</em></span> అని "
    "పేర్కొంటుంది; ఆ మూల సూచనను మార్చలేదు. మూలంలోని <span lang=\"en\">Saint Louis "
    "Iniversity</span> సంస్థ పేరు అక్షరదోషాన్ని కూడా యథాతథంగా ఉంచాం. పూర్తి పుస్తకం, "
    "సమాధానాల సూచిక, బయట ఉన్న వీడియోలు ఈ ప్యాకెట్‌లో ఉన్నాయని భావించవద్దు.</p>"
    "<p>తదుపరి మూల మాడ్యూల్: <span lang=\"en\">m82451, Chapter 1 Introduction</span>. "
    "అది ఈ ప్యాకెట్‌లో ఇంకా అనువదించలేదు.</p>"
    '<p><a href="source/m82630.en.cnxml" lang="en">Frozen English CNXML source</a> · '
    '<a href="translated/modules/m82630/index.cnxml">తెలుగు CNXML</a> · '
    '<a href="SOURCE_AND_CREDITS.json" lang="en">Source, asset and credit ledger</a> · '
    '<a href="EXPERT_REVIEW_LOG.json" lang="en">Terminology review ledger</a> · '
    '<a href="EDITORIAL_NOTES.md" lang="en">Editorial evidence and decisions</a> · '
    '<a href="LICENSE.txt" lang="en">CC BY-NC-SA 4.0 licence text</a></p>'
    '<p>నిర్దిష్ట మూలం: <a href="'
    + CANONICAL_SOURCE_URL
    + '" lang="en">OpenStax m82630 at the pinned commit</a>. మూల పుస్తకం: '
    '<a href="'
    + BOOK_URL
    + '" lang="en">OpenStax Elementary Algebra 2e</a>. '
    "ఇవి బాహ్య వెబ్ లింకులు; ఆఫ్‌లైన్ పఠనానికి అవసరం లేదు.</p></section></main>"
    '<footer><p lang="en">Original authors: Lynn Marecek; MaryAnne Anthony-Smith; '
    "Andrea Honeycutt Mathis. Copyright Rice University, OpenStax. "
    '<a href="'
    + LICENSE_URL
    + '">CC BY-NC-SA 4.0</a>, subject to component-specific notices. '
    "OpenStax and Rice University do not endorse this translation; their marks are not licensed.</p>"
    '<p lang="en">Translation and derivative build: OpenAI Codex gpt-5.6-sol, Ultra. '
    "All source and contributor credits are preserved. This complete preface packet is not a "
    "complete A10 edition or a validated Grades 3–10 mastery product.</p></footer></body></html>"
)
(ROOT / "index.html").write_text(page, encoding="utf-8")

# Exact structural and reader validation.
reader = LH.fromstring(page)
orig = E.fromstring(source_bytes)
assert len(list(orig.iter())) == len(list(doc.iter()))
assert [element.tag for element in orig.iter()] == [element.tag for element in doc.iter()]
ids0 = orig.xpath("//@id")
ids1 = doc.xpath("//@id")
assert ids0 == ids1 and len(ids0) == len(set(ids0))
for old, new in zip(orig.iter(), doc.iter()):
    attrs0 = {key: value for key, value in old.attrib.items() if key != "alt"}
    attrs1 = {
        key: value
        for key, value in new.attrib.items()
        if key not in ("alt", "{http://www.w3.org/XML/1998/namespace}lang")
    }
    assert attrs0 == attrs1
mathml_count = int(orig.xpath("count(//*[local-name()='math'])"))
assert mathml_count == int(doc.xpath("count(//*[local-name()='math'])")) == 0
source_exercises = len(orig.findall(".//c:exercise", NS))
source_solutions = int(orig.xpath("count(//*[local-name()='solution'])"))
assert source_exercises == source_solutions == 0
assert all(reader.xpath("//*[@id=$value]", value=source_id) for source_id in ids0)
reader_ids = reader.xpath("//@id")
assert len(reader_ids) == len(set(reader_ids))
local_links = []
external_links = []
for linked_element in reader.xpath("//*[@href or @src]"):
    value = linked_element.get("href") or linked_element.get("src")
    if value.startswith("#"):
        assert value[1:] in reader_ids, value
    else:
        parsed = urlparse(value)
        if parsed.scheme in ("http", "https"):
            assert parsed.scheme == "https" and parsed.netloc
            external_links.append(value)
            continue
        target_path = ROOT / (parsed.path or "index.html")
        assert target_path.is_file(), value
        if parsed.fragment:
            target_ids = (
                reader_ids
                if target_path.resolve() == (ROOT / "index.html").resolve()
                else LH.parse(str(target_path)).xpath("//@id")
            )
            assert parsed.fragment in target_ids, value
        local_links.append(value)

support_path = ROOT / "learning-support.html"
support_reader = LH.parse(str(support_path))
support_ids = support_reader.xpath("//@id")
assert len(support_ids) == len(set(support_ids))
for linked_element in support_reader.xpath("//*[@href or @src]"):
    value = linked_element.get("href") or linked_element.get("src")
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        assert parsed.scheme == "https" and parsed.netloc
    elif value.startswith("#"):
        assert value[1:] in support_ids, value
    else:
        target_path = ROOT / parsed.path
        assert target_path.is_file(), value
        if parsed.fragment:
            target_ids = LH.parse(str(target_path)).xpath("//@id")
            assert parsed.fragment in target_ids, value
assert not support_reader.xpath("//script|//iframe")

style_text = (ROOT / "style.css").read_text(encoding="utf-8")
assert "max-width:1050px" not in style_text
assert "header,main,footer{width:100%;max-width:none;margin:0 auto" in style_text
assert not reader.xpath("//script|//iframe")
assert not re.search(r"\ufffd|[\ud800-\udfff]", page)
assert all(
    re.search("[\u0c00-\u0c7f]", media.get("alt", ""))
    for media in doc.findall(".//c:media", NS)
)
assert all(
    (ROOT / "translated/modules/m82630" / image_element.get("src")).resolve().is_file()
    for image_element in doc.findall(".//c:image", NS)
)

visual_qa = read_json(ROOT / "VISUAL_QA.json")
replay_receipt = read_json(ROOT / "DETERMINISTIC_REPLAY.json")
assert visual_qa["schema"] == "a10.browser-visual-qa.v1"
assert replay_receipt["schema"] == "a10.deterministic-replay.v1"

qa = {
    "schema": "a10-locale-packet-qa-v1",
    "locale": "te-Telu-IN",
    "module": "m82630",
    "scope_status": "complete module packet; partial full-A10 assignment",
    "source_sha256": SOURCE_SHA,
    "translated_sha256": sha(translated_bytes),
    "checks": {
        "canonical_collection_modules": len(collection_modules),
        "collection_first_module": collection_modules[0],
        "collection_next_module": collection_modules[1],
        "full_source_slots_accounted": len(source_slots),
        "translated_slots": len(translated_keys),
        "credit_retained_slots": len(retained_keys),
        "every_translated_slot_contains_Telugu": True,
        "source_elements": len(list(orig.iter())),
        "same_element_order_and_namespace": True,
        "same_source_ids": len(ids0),
        "unique_source_ids": True,
        "all_source_ids_in_reader": True,
        "nonlinguistic_attributes_preserved": True,
        "MathML_count": mathml_count,
        "source_exercises": source_exercises,
        "source_solutions": source_solutions,
        "source_assets_verified": len(asset_records),
        "all_local_links_resolve": True,
        "standalone_learning_support_links_resolve": True,
        "local_link_references_checked": len(local_links),
        "external_https_link_references_checked": len(external_links),
        "all_4_media_alts_Telugu": True,
        "UTF8_no_replacement_or_surrogate_characters": True,
        "no_remote_render_dependencies": True,
        "full_page_centered_reflow_without_fixed_content_cap": True,
        "English_only_credit_paragraphs_have_lang_attribute": True,
        "source_asset_credit_ledger_present": True,
        "expert_review_schema_required_fields_present": True,
        "all_bridge_terms_covered_by_expert_review_log": len(covered_terms),
        "expert_review_rationale_is_explicitly_backfilled": all(
            entry["rationale_timing"] == "retrospective_reconstruction"
            for entry in expert_log["entries"]
        ),
        "authored_reading_checks": 3,
        "authored_rechecks": 3,
        "authored_answer_crosschecks": (
            "Compared explicitly with source eip-372 and para-00001; no invented source "
            "answer coverage."
        ),
    },
    "visual_QA": {
        "status": visual_qa["status"],
        "desktop": visual_qa["desktop"],
        "narrow": visual_qa["narrow"],
        "receipt_sha256": sha((ROOT / "VISUAL_QA.json").read_bytes()),
    },
    "deterministic_replay": {
        "status": replay_receipt["status"],
        "receipt_sha256": sha((ROOT / "DETERMINISTIC_REPLAY.json").read_bytes()),
        "command": "python build.py",
    },
    "limitations": [
        "No mathematical exercise or MathML appears in the source preface; this does not prove later-module math translation.",
        "Advanced algebra overview terminology remains editorial and provisional, not regional certification.",
        "The original English graph raster is retained, with full visible Telugu description and Telugu alt text.",
        "No audio or PDF reader is claimed for this bounded preface packet.",
        "Full A10 source translation and Grades 3–10 mastery workflow remain unfinished after this 1-of-82 increment.",
    ],
}
write_json(ROOT / "QA.json", qa)

owner_handoff = f"""# Owner handoff — Telugu A10 m82630

## Outcome

The complete canonical preface module `m82630` is translated into Telugu and packaged as one bounded successor increment. This is exactly one of 82 ordered A10 modules; it is not a full-book packet and does not claim the complete Grades 3–10 mastery workflow.

## Verified anchors

- Canonical commit: `{COMMIT}`
- Canonical source SHA-256: `{SOURCE_SHA}`
- Source/target accounting: {len(source_slots)} meaningful slots = {len(translated_keys)} translated + {len(retained_keys)} publication-credit slots retained
- CNXML: {len(list(orig.iter()))} elements, {len(ids0)} unique source IDs, {mathml_count} MathML elements, {source_exercises} exercises, {source_solutions} solutions
- Assets: {len(asset_records)} exact original rasters, each hash-locked; all four media elements have Telugu alt text
- Terminology ledger: complete for this packet; all {len(terms)} English-bridge terms map to an `EXPERT_REVIEW_LOG.json` decision. Every entry is labeled `retrospective_reconstruction`.
- Canon result: Telangana pages 26 and 85 support the whole-number/integer distinction. Andhra Pradesh evidence was not acquired and creates no hold. Advanced algebra labels remain explicit provisional choices.
- Visual QA: pass at 1280x900 and 390x844 for both the reader and standalone learning-support page; eight inspected PNG captures and exact hashes are recorded in `VISUAL_QA.json`.
- Deterministic replay: pass; two isolated exact-command rebuilds matched every packet path, byte count and SHA-256. See `DETERMINISTIC_REPLAY.json` and `PACKAGE.json`.
- Reflow and links: the reader fills the viewport without a fixed 1050px cap, and the separately packaged learning-support fragment links back to exact anchors in `index.html`.

## Integration boundary

Admit only this packet's owned files by exact hashes in `MANIFEST.json`/`CHECKSUMS.sha256`. Preserve the existing public predecessor and all unrelated locale/book paths. The package contains source, translated CNXML, semantic offline reader, four source assets, licence, provenance, terminology/review records, QA receipts, and learning support.

The builder confines its writes to this task-local packet. It does not update canonical or locale-control state; the owner performs any later control integration after rehashing this handoff.

## Next source action

Continue with `m82451` (Chapter 1 Introduction), canonical SHA-256 `025f994e3c66f19462c9423788f703f7987fecb67656911d840fdd15a58d8a4a`. Do not count the recovered A00 JSON files as A10 progress.
"""
(ROOT / "OWNER_HANDOFF.md").write_text(owner_handoff, encoding="utf-8")


def role_for(relative_path):
    if relative_path.startswith("source/"):
        return "frozen-source"
    if relative_path.startswith("translated/media/"):
        return "source-asset"
    if relative_path.startswith("translated/"):
        return "translated-source"
    if relative_path in {"index.html", "style.css", "learning-support.html"}:
        return "offline-reader"
    if relative_path in {"LICENSE.txt", "SOURCE_AND_CREDITS.json"}:
        return "rights-and-provenance"
    if relative_path in {"TERMINOLOGY.json", "EXPERT_REVIEW_LOG.json"}:
        return "terminology-and-review"
    if relative_path in {"QA.json", "VISUAL_QA.json", "DETERMINISTIC_REPLAY.json"}:
        return "qa-evidence"
    if relative_path.startswith("qa-screenshots/"):
        return "qa-evidence"
    if relative_path == "OWNER_HANDOFF.md":
        return "handoff"
    return "build-or-editorial-input"


payload_paths = sorted(
    path
    for path in ROOT.rglob("*")
    if path.is_file() and path.relative_to(ROOT).as_posix() not in EXCLUDED_FROM_PAYLOAD
)
payload_records = []
for path in payload_paths:
    relative = path.relative_to(ROOT).as_posix()
    data = path.read_bytes()
    payload_records.append(
        {
            "path": relative,
            "bytes": len(data),
            "sha256": sha(data),
            "role": role_for(relative),
        }
    )

manifest = {
    "schema": "a10-locale-module-manifest-v1",
    "locale": "te-Telu-IN",
    "module": "m82630",
    "scope": "complete preface module; partial full-A10 assignment (1/82)",
    "canonical_commit": COMMIT,
    "canonical_source_sha256": SOURCE_SHA,
    "files": payload_records,
    "manifest_note": (
        "MANIFEST.json, CHECKSUMS.sha256, PACKAGE.zip, and PACKAGE.json are excluded "
        "from the payload inventory to avoid self-reference; the ZIP contains the manifest "
        "and checksum ledger."
    ),
}
write_json(ROOT / "MANIFEST.json", manifest)

checksum_paths = payload_paths + [ROOT / "MANIFEST.json"]
checksum_paths = sorted(checksum_paths, key=lambda path: path.relative_to(ROOT).as_posix())
checksum_lines = [
    f"{sha(path.read_bytes())}  {path.relative_to(ROOT).as_posix()}"
    for path in checksum_paths
]
(ROOT / "CHECKSUMS.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

zip_paths = sorted(
    payload_paths + [ROOT / "MANIFEST.json", ROOT / "CHECKSUMS.sha256"],
    key=lambda path: path.relative_to(ROOT).as_posix(),
)
package_path = ROOT / "PACKAGE.zip"
with zipfile.ZipFile(package_path, "w") as archive:
    for path in zip_paths:
        relative = path.relative_to(ROOT).as_posix()
        info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        archive.writestr(info, path.read_bytes(), compresslevel=9)

with zipfile.ZipFile(package_path, "r") as archive:
    names = archive.namelist()
    assert names == [path.relative_to(ROOT).as_posix() for path in zip_paths]
    assert len(names) == len(set(names))
    for path, name in zip(zip_paths, names):
        assert archive.read(name) == path.read_bytes()

package_bytes = package_path.read_bytes()
package_receipt = {
    "schema": "a10.deterministic-package.v1",
    "locale": "te-Telu-IN",
    "module": "m82630",
    "file": "PACKAGE.zip",
    "bytes": len(package_bytes),
    "sha256": sha(package_bytes),
    "entry_count": len(zip_paths),
    "entries": [path.relative_to(ROOT).as_posix() for path in zip_paths],
    "entry_timestamp": "1980-01-01T00:00:00 (fixed ZIP metadata)",
    "compression": "DEFLATE level 9",
    "verification": "Every ZIP entry was read back and byte-compared with its source file.",
}
write_json(ROOT / "PACKAGE.json", package_receipt)

print(
    json.dumps(
        {
            "built": "m82630",
            "source_slots": len(source_slots),
            "ids": len(ids0),
            "elements": len(list(orig.iter())),
            "assets": len(asset_records),
            "reader_bytes": len(page.encode("utf-8")),
            "manifest_files": len(payload_records),
            "package_bytes": package_receipt["bytes"],
            "package_sha256": package_receipt["sha256"],
            "visual_QA": visual_qa["status"],
            "deterministic_replay": replay_receipt["status"],
            "next": "m82451",
        },
        ensure_ascii=False,
    )
)
