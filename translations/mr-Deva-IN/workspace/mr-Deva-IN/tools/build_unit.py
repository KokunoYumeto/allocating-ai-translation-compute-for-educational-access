"""Build a pinned Marathi unit as one offline HTML file.

Usage: python -B mr-Deva-IN/tools/build_unit.py MR-BRIDGE-002
The config and provenance lock are authored/reviewed inputs, not inferred truth.
Exact displayed-math checks are regressions, not independent mathematical proof.
This builder intentionally does not alter the legacy MR-BRIDGE-001 builder.
"""
import argparse
import base64
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import unicodedata
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
UNIT_RE = re.compile(r"MR-BRIDGE-[0-9]{3}\Z")
ID_RE = re.compile(r"[^\s#]+\Z")
TAGS = frozenset("article section aside nav header footer div p h1 h2 h3 h4 h5 h6 "
                 "ol ul li dl dt dd span a strong em b i small sup sub code pre "
                 "br hr table caption thead tbody tfoot tr th td figure figcaption "
                 "blockquote details summary cite abbr q dfn mark s kbd samp time "
                 "del ins bdi bdo wbr address img".split())
ATTRS = frozenset("id class lang title role dir href colspan rowspan scope headers "
                  "start reversed value open".split())
COUNT_KEYS = ("source_count", "translated_worked_examples", "translated_definitions",
              "original_practice_items")
OPTIONAL_COUNT_KEYS = ("translated_practice_items", "translated_resource_notes")
ASSET_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,199}\.(?:jpe?g|png)\Z", re.I)
IMAGE_STYLE = (b"/* Only included for pinned raster-image units. */\n"
               b"figure img { display:block; max-width:100%; height:auto; margin:16px auto; }\n"
               b"figure { margin:24px 0; }\n"
               b"figcaption { line-height:1.65; color:var(--muted); }\n")


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inside(base, relative):
    """Reject traversal, Windows drive/UNC syntax, and escaping symlinks."""
    require(isinstance(relative, str) and relative, "empty or invalid relative path")
    require("\\" not in relative and ":" not in relative, "unsafe relative path")
    parts = PurePosixPath(relative)
    require(not parts.is_absolute() and all(p not in ("", ".", "..")
            for p in relative.split("/")), "unsafe relative path")
    target = base.joinpath(*parts.parts).resolve()
    require(target.is_relative_to(base), "path escapes unit base")
    return target


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=lambda value: require(False, f"invalid JSON number: {value}"))
    require(isinstance(value, dict), f"JSON object required: {path.name}")
    return value, raw


def validate_text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"empty or invalid {label}")
    require(unicodedata.normalize("NFC", value) == value, f"non-NFC {label}")
    require("\ufffd" not in value, f"replacement character in {label}")


def validate_style(style):
    # No asset loading, CSS escape obfuscation, or raw HTML in the shared sheet.
    plain = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    require("\\" not in plain and "<" not in style, "unsafe stylesheet")
    require(not re.search(r"url\s*\(|@\s*import\b|expression\s*\(|-moz-binding|behavior\s*:",
                          plain, re.I), "external or executable stylesheet dependency")


def validate_asset_config(config):
    assets = config.get("assets", {})
    require(isinstance(assets, dict), "assets must be an object keyed by file ID")
    for asset_id, record in assets.items():
        require(ASSET_ID_RE.fullmatch(asset_id) and ".." not in asset_id, "invalid asset ID")
        require(isinstance(record, dict), f"invalid asset record: {asset_id}")
        require(isinstance(record.get("sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]), f"invalid asset SHA-256: {asset_id}")
        require(record.get("mime") in ("image/jpeg", "image/png"), f"unsupported asset MIME: {asset_id}")
        expected_mime = "image/png" if asset_id.lower().endswith(".png") else "image/jpeg"
        require(record["mime"] == expected_mime, f"asset ID/MIME mismatch: {asset_id}")
    return assets


def validate_markup(root, assets):
    links = []
    external_links = 0
    images = []
    parents = {child: parent for parent in root.iter() for child in parent}
    for node in root.iter():
        require(node.tag in TAGS, f"unsupported or executable element: {node.tag}")
        require("source-label" not in node.get("class", "").split(),
                "source labels are generated, not authored")
        for key in node.attrib:
            require(key in ATTRS or (node.tag == "img" and key in ("src", "alt"))
                    or re.fullmatch(r"(?:data|aria)-[a-z][a-z0-9-]*", key),
                    f"unsupported or executable attribute: {key}")
        if node.tag == "img":
            source = node.get("src", "")
            require(source.startswith("asset:") and ASSET_ID_RE.fullmatch(source[6:]),
                    "unsupported or executable image source; use configured asset:ID")
            asset_id = source[6:]
            require(asset_id in assets, f"image asset is not configured: {asset_id}")
            validate_text(node.get("alt"), "image alt text")
            require(len(node) == 0 and not (node.text or "").strip(), "img must be an empty XML element")
            ancestor = parents.get(node)
            while ancestor is not None and ancestor.tag != "figure":
                ancestor = parents.get(ancestor)
            require(ancestor is not None and ancestor.get("id"), "image needs an identified figure ancestor")
            images.append((node, asset_id))
        if "href" in node.attrib:
            require(node.tag == "a", "href only allowed on citation/navigation anchors")
            href = node.get("href")
            if href.startswith("#"):
                links.append(href[1:])
            else:
                # These are optional citations, never automatically fetched assets.
                require(bool(re.fullmatch(r"https://[^\s/]+(?:/[^\s]*)?", href)),
                        "only same-document links and HTTPS citations are supported")
                external_links += 1
    require({asset_id for _, asset_id in images} == set(assets), "configured assets must all be used")
    return links, external_links, images


def load_pinned_assets(assets, witnesses, base, images):
    """Read only configured, witnessed files; preserve their bytes in data URLs.

    Magic-byte checks distinguish supported formats; they do not decode images
    or replace the separate visual check of complete original source diagrams.
    """
    pins = {(item["path"], item["sha256"]) for item in witnesses}
    urls = {}
    records = []
    paths = set()
    for asset_id in sorted(assets):
        asset = assets[asset_id]
        path = inside(base, asset.get("path"))
        require(path not in paths, "duplicate asset path")
        paths.add(path)
        require((asset["path"], asset["sha256"]) in pins, f"asset is not pinned in provenance: {asset_id}")
        raw = path.read_bytes()
        require(sha(raw) == asset["sha256"], f"asset byte drift: {asset_id}")
        signature = b"\x89PNG\r\n\x1a\n" if asset["mime"] == "image/png" else b"\xff\xd8\xff"
        require(raw.startswith(signature), f"asset MIME/magic mismatch: {asset_id}")
        urls[asset_id] = "data:" + asset["mime"] + ";base64," + base64.b64encode(raw).decode("ascii")
        records.append({"id": asset_id, "path": asset["path"], "sha256": asset["sha256"],
                        "mime": asset["mime"], "bytes": len(raw),
                        "uses": sum(used_id == asset_id for _, used_id in images)})
    return urls, records


def anchor_targets(node):
    return {a.get("href") for a in node.iter("a") if "".join(a.itertext()).strip()}


class RenderedLabels(HTMLParser):
    """Check actual serialized labels, rather than assuming insertion worked."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.labels = []
        self.label_tag = None
        self.label_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "source-label" in attrs.get("class", "").split():
            require(self.label_tag is None, "nested rendered source label")
            require(attrs.get("lang") == "en", "rendered source-label language drift")
            self.label_tag = tag
            self.label_text = []

    def handle_data(self, data):
        if self.label_tag is not None:
            self.label_text.append(data)

    def handle_endtag(self, tag):
        if tag == self.label_tag:
            self.labels.append("".join(self.label_text))
            self.label_tag = None


def write_outputs(outputs):
    """Stage both small artifacts before replacing either existing checkpoint.

    A disk-full staging failure cannot truncate old artifacts. The two replaces
    are not a filesystem transaction; their hashes detect an interrupted pair.
    """
    pending = []
    try:
        for target, data in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=target.name + ".",
                                             suffix=".tmp", delete=False) as handle:
                pending.append((Path(handle.name), target))
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        for temporary, target in pending:
            os.replace(temporary, target)
    finally:
        for temporary, _ in pending:
            if temporary.exists():
                temporary.unlink()


def build(unit, base=BASE):
    """Validate inputs and write deterministic HTML/receipt; return the receipt."""
    require(isinstance(unit, str) and UNIT_RE.fullmatch(unit), "invalid unit name")
    base = Path(base).resolve()
    require(base.is_dir(), "unit base does not exist")
    source_path = inside(base, f"translations/{unit}.xml")
    config, config_raw = read_json(inside(base, f"units/{unit}.json"))
    lock, lock_raw = read_json(inside(base, f"provenance/{unit}.lock.json"))
    output = inside(base, f"output/{unit}.html")
    receipt_path = inside(base, f"qa/{unit}-build-receipt.json")
    for key in COUNT_KEYS:
        require(type(config.get(key)) is int and config[key] >= 0, f"invalid count: {key}")
    for key in OPTIONAL_COUNT_KEYS:
        require(type(config.get(key, 0)) is int and config.get(key, 0) >= 0, f"invalid count: {key}")
    validate_text(config.get("title"), "title")
    require(config["translated_worked_examples"] + config["translated_definitions"]
            + sum(config.get(key, 0) for key in OPTIONAL_COUNT_KEYS)
            <= config["source_count"], "source classification counts exceed source count")
    question_ids = config.get("question_ids")
    require(isinstance(question_ids, list), "question_ids must be a list")
    require(all(isinstance(q, str) and ID_RE.fullmatch(q) and not q.startswith("S-")
                for q in question_ids), "invalid question ID")
    require(len(question_ids) == len(set(question_ids)), "duplicate question ID")
    require(len(question_ids) == config["original_practice_items"], "question count drift")
    expected = config.get("expected_math")
    require(isinstance(expected, dict), "expected_math must be a map")
    for key, value in expected.items():
        validate_text(key, "math-check key")
        validate_text(value, "expected mathematical chain")
    terms = config.get("required_terms")
    require(isinstance(terms, list), "required_terms must be a list")
    for term in terms:
        validate_text(term, "required term")
    require(len(terms) == len(set(terms)), "duplicate required term")
    assets = validate_asset_config(config)

    raw = source_path.read_bytes()
    xml = raw.decode("utf-8")
    validate_text(xml, "translation")
    require("<!DOCTYPE" not in xml and "<!ENTITY" not in xml, "XML declarations/entities prohibited")
    root = ET.fromstring(raw)
    require(root.tag == "article" and root.get("id") == unit, "wrong article/unit ID")
    require(root.get("lang") == "mr-Deva-IN", "wrong locale")
    text = "".join(root.itertext())
    nodes = [node for node in root.iter() if "id" in node.attrib]
    ids = [node.get("id") for node in nodes]
    require(all(ID_RE.fullmatch(item) for item in ids), "empty or invalid XML/HTML ID")
    require(len(ids) == len(set(ids)), "duplicate XML/HTML IDs")
    by_id = dict(zip(ids, nodes))
    links, external_links, images = validate_markup(root, assets)
    require(all(link in by_id for link in links), "broken answer/navigation link")
    solutions = {"S-" + question for question in question_ids}
    require({item for item in ids if item.startswith("S-")} == solutions,
            "missing or unexpected question/solution targets")
    # D/P/Q numeric IDs are reserved for the explicit question inventory.
    require({item for item in ids if re.fullmatch(r"[DPQ][1-9][0-9]*", item)} <= set(question_ids),
            "unlisted original question target")
    for question in question_ids:
        require(question in by_id, f"missing question target: {question}")
        answer = "S-" + question
        require("#" + answer in anchor_targets(by_id[question]),
                f"missing bidirectional question/answer anchor: {question}")
        require("#" + question in anchor_targets(by_id[answer]),
                f"missing bidirectional question/answer anchor: {answer}")

    selections = lock.get("source_selections")
    require(isinstance(selections, list) and all(isinstance(s, dict) for s in selections),
            "source_selections must be a list of objects")
    for selection in selections:
        validate_text(selection.get("locator"), "source locator")
        validate_text(selection.get("target_id"), "original source ID")
        require("#" in selection["locator"]
                and selection["locator"].rsplit("#", 1)[-1] == selection["target_id"],
                "source locator/original ID mismatch")
    source_nodes = [node for node in root.iter() if "data-source" in node.attrib]
    sources = [node.get("data-source") for node in source_nodes]
    require(sources == [s["locator"] for s in selections], "source selection drift")
    require(len(sources) == config["source_count"], "source count drift")
    require(len(sources) == len(set(sources)), "duplicate source locator")
    for node, selection in zip(source_nodes, selections):
        require(node.get("id") == selection["target_id"], "source ID not preserved on source block")

    witnesses = lock.get("witnesses")
    require(isinstance(witnesses, list) and all(isinstance(w, dict) for w in witnesses),
            "witnesses must be a list of objects")
    require(not sources or witnesses, "source selections require pinned witnesses")
    witness_paths = []
    for witness in witnesses:
        path = inside(base, witness.get("path"))
        require(isinstance(witness.get("sha256"), str)
                and re.fullmatch(r"[0-9a-f]{64}", witness["sha256"]), "invalid witness SHA-256")
        require(sha(path.read_bytes()) == witness["sha256"], f"witness drift: {witness['path']}")
        witness_paths.append(path)
    require(len(witness_paths) == len(set(witness_paths)), "duplicate witness path")
    asset_urls, asset_records = load_pinned_assets(assets, witnesses, base, images)

    actual = {}
    for node in root.iter():
        if "data-check" in node.attrib:
            key = node.get("data-check")
            require(key not in actual, f"duplicate data-check key: {key}")
            actual[key] = "".join(node.itertext())
    require(actual == expected, "displayed mathematical chain changed; review and revalidate")
    for term in terms:
        require(term in text, f"required term missing: {term}")
    style_names = ["tools/reader.css"]
    if inside(base, "tools/unit-reader.css").is_file():
        style_names.append("tools/unit-reader.css")
    style_parts = [inside(base, name).read_bytes() for name in style_names]
    style_raw = b"\n".join(style_parts)
    if assets:
        style_raw += b"\n" + IMAGE_STYLE
    style = style_raw.decode("utf-8")
    validate_style(style)
    for block in source_nodes:
        # Paragraph-like source fragments need a phrasing label, not nested <p>.
        tag = "p" if block.tag in {"article", "section", "div", "aside", "figure", "li", "dd"} else "span"
        if tag == "span":
            ET.SubElement(block, "br")
        label = ET.SubElement(block, tag, {"class": "source-label", "lang": "en"})
        label.text = "Source: " + block.get("data-source")
    for node, asset_id in images:
        node.set("src", asset_urls[asset_id])
    body = ET.tostring(root, encoding="unicode", method="html")
    image_policy = "img-src data:; " if assets else ""
    document = ('<!doctype html>\n<html lang="mr-Deva-IN"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
                + image_policy + 'style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
                '<title>' + html.escape(config["title"]) + '</title><style>'
                + style + '</style></head><body>' + body + '</body></html>\n')
    rendered = RenderedLabels()
    rendered.feed(document)
    rendered.close()
    require(rendered.label_tag is None and rendered.labels == ["Source: " + s for s in sources],
            "rendered source-label drift")
    html_bytes = document.encode("utf-8")
    receipt = {
        "unit": unit, "locale": "mr-Deva-IN", "result": "PASS",
        "source_sha256": sha(raw), "config_sha256": sha(config_raw),
        "provenance_lock_sha256": sha(lock_raw), "stylesheet_sha256": sha(style_raw),
        "stylesheet_files": [{"path": name, "sha256": sha(data)}
                             for name, data in zip(style_names, style_parts)],
        "html_sha256": sha(html_bytes), "html_bytes": len(html_bytes),
        "embedded_image_count": len(images), "distinct_embedded_assets": len(asset_records),
        "embedded_image_raw_bytes": sum(item["bytes"] * item["uses"] for item in asset_records),
        "distinct_asset_bytes": sum(item["bytes"] for item in asset_records),
        "embedded_assets": asset_records,
        "selected_source_blocks": len(sources),
        "translated_worked_examples": config["translated_worked_examples"],
        "translated_definitions": config["translated_definitions"],
        "translated_practice_items": config.get("translated_practice_items", 0),
        "translated_resource_notes": config.get("translated_resource_notes", 0),
        "unclassified_source_blocks": (len(sources) - config["translated_worked_examples"]
                                       - config["translated_definitions"]
                                       - sum(config.get(key, 0) for key in OPTIONAL_COUNT_KEYS)),
        "original_practice_items": len(question_ids), "question_answer_pairs": len(question_ids),
        "displayed_math_regressions": len(actual), "local_links_checked": len(links),
        "optional_external_citation_links": external_links, "unique_ids": len(ids),
        "source_labels_checked": len(rendered.labels), "pinned_witnesses_checked": len(witnesses),
        "required_terms_checked": len(terms),
        "devanagari_characters": len(re.findall("[\u0900-\u097f]", text)),
        "checks": ["XML well-formedness", "NFC Unicode", "exact locale and unit ID", "unique IDs",
                   "local links and bidirectional question/answer anchors", "ordered source locators",
                   "original source IDs on corresponding blocks", "pinned witness SHA-256",
                   "exact displayed-math regression (not independent proof)", "required terms",
                   "rendered source labels", "no script, external runtime, font or media dependency"],
        "not_claimed": ["independent mathematical proof", "semantic verification of all prose",
                        "human expert or native-speaker approval", "complete source-module translation",
                        "independently inferred example/definition classifications", "visual browser QA"],
    }
    if assets:
        receipt["generated_image_styles_sha256"] = sha(IMAGE_STYLE)
        receipt["checks"].append("configured JPEG/PNG bytes, MIME magic, provenance pins and nonempty alt text")
        receipt["not_claimed"].append("complete image decoding or correctness of alt descriptions")
    receipt_bytes = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_outputs(((output, html_bytes), (receipt_path, receipt_bytes)))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit", help="unit ID, for example MR-BRIDGE-002")
    args = parser.parse_args()
    try:
        receipt = build(args.unit)
    except (ValueError, OSError, ET.ParseError) as error:
        parser.exit(1, f"Build failed: {error}\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
