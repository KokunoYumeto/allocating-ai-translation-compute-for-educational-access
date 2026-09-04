"""Read-only structural/content checks for exact m81244 remainder unit TE-B020.

The checker derives the module partition from the pinned canonical XML and the
nine already frozen content roots. It does not call a builder or write output.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from inspect_source import slots


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
CN = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
XH = "{http://www.w3.org/1999/xhtml}"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
MODULE_PATH = ROOT / "downloads/upstream-prealgebra/modules/m81244/index.cnxml"
MODULE_BYTES = 119_141
MODULE_SHA = "b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b"
MODULE_BLOB = "1c3617fd0547029c883126348113f437395d718b"
SOURCE_SHA = "bda74b9e18a5bb466709b01e569d6511c265606dd1c0eefd178c1815064ac91d"
UUID = "8069044b-6fb1-49bf-b03a-64988f9b1ddd"

CONTENT_UNITS = (
    ("TE-B011", "fs-id2299412", 18, 8, "cdd73289f869830dcc51fb3df012c1b50d5ef191698dcfbea244d39dbc45cb83"),
    ("TE-B012", "fs-id1122444", 13, 6, "9b680f02649625b9263c6fa2bc9aa9defaa93d94fec588ea203c7bbc7f291287"),
    ("TE-B013", "fs-id2601285", 143, 93, "dc2f2c8ad88edb588df364026e9e5b4301d416ef641fc7c833d5ca4fe0f93b35"),
    ("TE-B014", "fs-id2145437", 322, 171, "b865a80cc39efa14f98ddd39d05d2ff688439978b39d9e153533254c9ad91352"),
    ("TE-B015", "fs-id1385496", 1480, 859, "8fc54e5e660bd66b25739144d64fd172a61da3b1407449c1ed066dde75c5034b"),
    ("TE-B016", "fs-id2691382", 273, 148, "a185ed309ff878a6d29a714fabb8d3986c6020a82dbc7c99d89b2eb8f135aa0f"),
    ("TE-B017", "fs-id2197427", 210, 114, "749a7764e3df7024919ddf26db57a6ad1c6628aa8b44929a204527d58ea746cf"),
    ("TE-B018", "fs-id1611455", 81, 53, "2ed4ba3ccb103953b8df710aacd5c956f26563c1c5fb6da2429ac138058b1a82"),
    ("TE-B019", "fs-id2263283", 1017, 494, "5c0d3d631bb07b5f2251bb72018f9f6b9b530f63d9bed26857b7c66ffb335275"),
)

OBJECTIVES = (
    "సంకలనాన్ని చిహ్నాలతో రాయడం",
    "పూర్ణాంకాల సంకలనాన్ని నమూనాలతో చూపడం",
    "నమూనాలు లేకుండా పూర్ణాంకాలను కలపడం",
    "మాటల్లో ఇచ్చినదాన్ని గణిత సంకేతాలతో రాయడం",
    "జీవిత సందర్భాల సమస్యల్లో పూర్ణాంకాలను కలపడం",
)
TRANSLATIONS = {
    "s001": "పూర్ణాంకాలను కలపడం",
    "s003": "పూర్ణాంకాలను కలపడం",
    "s004": "ఈ పాఠభాగం పూర్తయ్యేసరికి మీరు చేయగలిగేవి:",
    "s005": OBJECTIVES[0],
    "s006": OBJECTIVES[1],
    "s007": OBJECTIVES[2],
    "s008": OBJECTIVES[3],
    "s009": OBJECTIVES[4],
    "s011": "మొత్తం (sum)",
    "s012": "రెండు లేదా అంతకంటే ఎక్కువ సంఖ్యలను కలిపితే వచ్చే ఫలితమే మొత్తం.",
}
PROTECTED = {
    "s002": {"tag": MD + "content-id", "value": "m81244", "reason": "Canonical module identifier; not prose."},
    "s010": {"tag": MD + "uuid", "value": UUID, "reason": "Canonical module UUID; not prose."},
}
LINKS = (
    ("TE-B013.html#fs-id2601285", OBJECTIVES[0]),
    ("TE-B014.html#fs-id2145437", OBJECTIVES[1]),
    ("TE-B015.html#fs-id1385496", OBJECTIVES[2]),
    ("TE-B016.html#fs-id2691382", OBJECTIVES[3]),
    ("TE-B017.html#fs-id2197427", OBJECTIVES[4]),
    ("TE-B018.html#fs-id1611455", None),
    ("TE-B019.html#fs-id2263283", None),
)


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_of(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def ids_of(root: ET.Element) -> dict[str, ET.Element]:
    pairs = [(node.get("id"), node) for node in root.iter() if node.get("id")]
    need(len(pairs) == len({key for key, _ in pairs}), "Duplicate XML ID")
    return dict(pairs)


def signature(node: ET.Element):
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text,
        node.tail,
        tuple(signature(child) for child in node),
    )


def detached_signature(node: ET.Element):
    clone = copy.deepcopy(node)
    clone.tail = None
    return signature(clone)


def structure(root: ET.Element):
    return tuple((node.tag, tuple(sorted(node.attrib.items())), len(node)) for node in root.iter())


def module_baseline() -> ET.Element:
    raw = MODULE_PATH.read_bytes()
    need(len(raw) == MODULE_BYTES and sha(raw) == MODULE_SHA, "Pinned m81244 bytes/hash changed")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(blob == MODULE_BLOB, "Pinned m81244 Git blob changed")
    lock = json.loads((BASE / "sources.lock.json").read_text("utf-8"))
    rows = [row for row in lock["source_files"] if row["course"] == "A00" and row["module"] == "m81244" and row["role"] == "canonical_english"]
    need(rows == [{"course": "A00", "module": "m81244", "role": "canonical_english", "path": "downloads/upstream-prealgebra/modules/m81244/index.cnxml", "bytes": MODULE_BYTES, "sha256": MODULE_SHA}], "m81244 source-lock record changed")
    root = ET.fromstring(raw)
    validate_module_graph(root)
    return root


def validate_module_graph(root: ET.Element) -> dict[str, int]:
    need(root.tag == CN + "document" and not root.attrib, "Canonical module wrapper changed")
    need([child.tag for child in root] == [CN + "title", CN + "metadata", CN + "content", CN + "glossary"], "Canonical direct-child order changed")
    need(root.findtext(CN + "title") == "Add Whole Numbers", "Canonical module title changed")
    need(root.findtext(CN + "metadata/" + MD + "content-id") == "m81244", "Canonical content ID changed")
    need(root.findtext(CN + "metadata/" + MD + "uuid") == UUID, "Canonical UUID changed")
    content = root.find(CN + "content")
    need(content is not None and [child.get("id") for child in content] == [row[1] for row in CONTENT_UNITS], "Canonical content-root order changed")
    need((len(list(root.iter())), len(list(slots(root))), len(ids_of(root))) == (3576, 1958, 756), "Canonical module count changed")
    return {"module_elements": 3576, "module_slots": 1958, "module_ids": 756}


def source_baseline() -> tuple[ET.Element, dict, ET.Element]:
    module = module_baseline()
    raw = (BASE / "sources/TE-B020.en.cnxml").read_bytes()
    need(sha(raw) == SOURCE_SHA, "Frozen B020 source hash changed")
    source = ET.fromstring(raw)
    metadata = json.loads((BASE / "sources/TE-B020.source.json").read_text("utf-8"))
    validate_remainder_source(source, metadata, module)
    return source, metadata, module


def validate_remainder_source(source: ET.Element, metadata: dict, module: ET.Element) -> dict[str, int]:
    need(metadata["unit"] == "TE-B020" and metadata["module"] == "m81244" and metadata["section"] == "@module-remainder", "B020 source metadata identity changed")
    need(metadata["source_commit"] == COMMIT and metadata["source_sha256"] == SOURCE_SHA, "B020 source provenance changed")
    need(metadata["protected_slots"] == PROTECTED, "B020 protected source metadata changed")
    need(source.tag == module.tag and source.attrib == module.attrib and source.text == module.text, "B020 document wrapper differs")
    need([node.tag for node in source] == [CN + "title", CN + "metadata", CN + "content", CN + "glossary"], "B020 child order changed")
    for name in ("title", "metadata", "glossary"):
        need(signature(source.find(CN + name)) == signature(module.find(CN + name)), f"B020 {name} differs from canonical")
    actual_content = source.find(CN + "content")
    canonical_content = module.find(CN + "content")
    need(actual_content is not None and canonical_content is not None, "Missing content wrapper")
    need((actual_content.tag, actual_content.attrib, actual_content.text, actual_content.tail) == (canonical_content.tag, canonical_content.attrib, canonical_content.text, canonical_content.tail), "Content wrapper metadata changed")
    need(len(actual_content) == 0, "B020 content wrapper duplicates lesson content")
    need((len(list(source.iter())), len(list(slots(source))), len(ids_of(source))) == (19, 12, 4), "B020 19/12/4 inventory changed")
    need(list(ids_of(source)) == ["para-00001", "list-00001", "fs-id1226736", "fs-id1245763"], "B020 ID order changed")
    for name in ("exercise", "problem", "solution", "media", "image"):
        need(not list(source.iter(CN + name)), f"B020 unexpectedly contains {name}")
    need(not list(source.iter(MATH + "math")), "B020 unexpectedly contains MathML")
    return validate_coverage(module, source, metadata)


def validate_coverage(module: ET.Element, source: ET.Element, metadata: dict) -> dict[str, int]:
    content = module.find(CN + "content")
    need(content is not None and len(content) == len(CONTENT_UNITS), "Canonical content partition changed")
    coverage_rows = metadata.get("coverage", {}).get("content_units", [])
    expected_meta = [
        {"unit": unit, "source_id": ident, "elements": elements, "text_slots": count, "source_sha256": source_hash}
        for unit, ident, elements, count, source_hash in CONTENT_UNITS
    ]
    need(coverage_rows == expected_meta, "B020 coverage metadata rows changed")
    content_elements = 0
    content_slots = 0
    frozen_ids: set[str] = set()
    for canonical_child, (unit, ident, elements, count, source_hash) in zip(content, CONTENT_UNITS):
        need(canonical_child.get("id") == ident, f"Canonical child mismatch for {unit}")
        path = BASE / "sources" / f"{unit}.en.cnxml"
        raw = path.read_bytes()
        unit_meta = json.loads((BASE / "sources" / f"{unit}.source.json").read_text("utf-8"))
        need(sha(raw) == source_hash == unit_meta["source_sha256"], f"Frozen hash mismatch for {unit}")
        frozen = ET.fromstring(raw)
        need(signature(frozen) == detached_signature(canonical_child), f"Frozen graph mismatch for {unit}")
        need((len(list(frozen.iter())), len(list(slots(frozen)))) == (elements, count), f"Frozen count mismatch for {unit}")
        need((unit_meta["element_count"], unit_meta["text_slots"], unit_meta["section"]) == (elements, count, ident), f"Frozen metadata mismatch for {unit}")
        unit_ids = set(ids_of(frozen))
        need(not frozen_ids & unit_ids, f"Cross-unit duplicate ID in {unit}")
        frozen_ids.update(unit_ids)
        content_elements += elements
        content_slots += count
    remainder_ids = set(ids_of(source))
    need(not frozen_ids & remainder_ids, "B020 duplicates an ID from B011-B019")
    module_elements = len(list(module.iter()))
    module_slots = len(list(slots(module)))
    remainder_elements = len(list(source.iter()))
    remainder_slots = len(list(slots(source)))
    need((content_elements, content_slots) == (3557, 1946), "B011-B019 coverage sum changed")
    need((remainder_elements, remainder_slots) == (19, 12), "B020 remainder sum changed")
    need(content_elements + remainder_elements == module_elements == 3576, "3557+19 element coverage proof failed")
    need(content_slots + remainder_slots == module_slots == 1958, "1946+12 slot coverage proof failed")
    return {"content_elements": content_elements, "content_slots": content_slots, "remainder_elements": remainder_elements, "remainder_slots": remainder_slots, "module_elements": module_elements, "module_slots": module_slots}


def catalog_baseline() -> dict:
    catalog = json.loads((BASE / "translations/TE-B020.te.json").read_text("utf-8"))
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict) -> None:
    need(catalog["schema"] == "te-cnxml-unit-localization-v2" and catalog["unit_id"] == "TE-B020" and catalog["module_id"] == "m81244", "B020 catalog identity changed")
    need(catalog["section_id"] == "@module-remainder" and catalog["source_commit"] == COMMIT, "B020 catalog provenance changed")
    need(catalog["expected_text_slot_count"] == 12, "B020 catalog slot count changed")
    need(catalog["protected_slots"] == PROTECTED, "B020 catalog protected slots changed")
    need(catalog["translations"] == TRANSLATIONS, "B020 exact translations changed")
    need(set(catalog["translations"]) | set(catalog["protected_slots"]) == {f"s{i:03}" for i in range(1, 13)}, "B020 slot coverage changed")
    need(not set(catalog["translations"]) & set(catalog["protected_slots"]), "Protected slot also translated")


def localize_catalog(source: ET.Element, catalog: dict) -> ET.Element:
    validate_catalog(catalog)
    target = copy.deepcopy(source)
    items = list(slots(target))
    need(len(items) == 12, "B020 source slot count changed before localization")
    for index, (element, field, value) in enumerate(items, 1):
        key = f"s{index:03}"
        if key in catalog["protected_slots"]:
            protected = catalog["protected_slots"][key]
            need(element.tag == protected["tag"] and field == "text" and value == protected["value"], f"Protected slot {key} changed")
        else:
            setattr(element, field, catalog["translations"][key])
    return target


def validate_target(source: ET.Element, target: ET.Element, catalog: dict) -> dict[str, int]:
    validate_catalog(catalog)
    need(structure(target) == structure(source), "B020 target structure/IDs/attributes changed")
    need((len(list(target.iter())), len(list(slots(target))), len(ids_of(target))) == (19, 12, 4), "B020 target 19/12/4 inventory changed")
    items = list(slots(target))
    for index, (element, field, value) in enumerate(items, 1):
        key = f"s{index:03}"
        if key in PROTECTED:
            need(element.tag == PROTECTED[key]["tag"] and field == "text" and value == PROTECTED[key]["value"], f"Protected target slot {key} changed")
        else:
            need(value == TRANSLATIONS[key], f"Translated target slot {key} changed")
    need(target.findtext(CN + "title") == target.findtext(CN + "metadata/" + MD + "title") == "పూర్ణాంకాలను కలపడం", "Translated title pair changed")
    objective_nodes = target.findall(CN + "metadata/" + MD + "abstract/" + CN + "list/" + CN + "item")
    need(tuple(node.text for node in objective_nodes) == OBJECTIVES, "Five objective ordering/wording changed")
    need(len(target.find(CN + "content")) == 0, "Localized content wrapper duplicates lesson content")
    glossary = target.find(CN + "glossary")
    definitions = glossary.findall(CN + "definition") if glossary is not None else []
    need(len(definitions) == 1 and definitions[0].get("id") == "fs-id1226736", "Glossary definition count/ID changed")
    need([node.tag for node in definitions[0]] == [CN + "term", CN + "meaning"], "Glossary term/meaning order changed")
    need(definitions[0].findtext(CN + "term") == "మొత్తం (sum)", "Glossary term changed")
    meaning = definitions[0].find(CN + "meaning")
    need(meaning is not None and meaning.get("id") == "fs-id1245763" and meaning.text == TRANSLATIONS["s012"], "Glossary meaning changed")
    for name in ("exercise", "problem", "solution", "media", "image"):
        need(not list(target.iter(CN + name)), f"Localized B020 unexpectedly contains {name}")
    need(not list(target.iter(MATH + "math")), "Localized B020 unexpectedly contains MathML")
    return {"target_elements": 19, "target_slots": 12, "target_ids": 4, "localized_slots": 10, "protected_slots": 2, "objectives": 5, "glossary_definitions": 1}


def bridge_baseline() -> ET.Element:
    bridge = ET.parse(BASE / "translations/TE-B020.bridge.xhtml").getroot()
    validate_bridge(bridge)
    return bridge


def validate_bridge(bridge: ET.Element) -> dict[str, int]:
    need(bridge.tag == XH + "section" and bridge.get("id") == "B020-bridge" and bridge.get("lang") == "te", "B020 bridge root changed")
    ids = list(ids_of(bridge))
    need(ids == ["B020-bridge", "B020-disclosure", "B020-source-boundary", "B020-objective-links", "B020-sum-gloss", "B020-boundary"], "B020 bridge IDs/order changed")
    forbidden = {"script", "form", "iframe", "img", "svg", "table", "details", "input", "button"}
    need(not any(node.tag.rsplit("}", 1)[-1] in forbidden for node in bridge.iter()), "Bridge duplicates lesson/assessment/media structure")
    link_nodes = [node for node in bridge.iter(XH + "a")]
    need(tuple(node.get("href") for node in link_nodes) == tuple(link for link, _ in LINKS), "B020 bridge links/order changed")
    objective_section = ids_of(bridge)["B020-objective-links"]
    items = objective_section.findall(XH + "ul/" + XH + "li")
    need(len(items) == 5, "B020 objective-link item count changed")
    for item, (href, objective) in zip(items, LINKS[:5]):
        anchor = item.find(XH + "a")
        need(anchor is not None and anchor.get("href") == href and objective in text_of(item), "Objective/link mapping changed")
    for href, _ in LINKS:
        filename, fragment = href.split("#", 1)
        source_path = BASE / "sources" / (filename.removesuffix(".html") + ".en.cnxml")
        need(source_path.exists() and fragment in ids_of(ET.parse(source_path).getroot()), "Bridge link target missing: " + href)
    text = text_of(bridge)
    need("కొత్త పాఠం, ప్రశ్నల సమితి, మార్కుల ప్రమాణం" in text, "Original/no-score disclosure changed")
    need("పునరావృతం నివారించామని" in text and "తొమ్మిది మూల ఉపభాగాలు" in text, "Empty-wrapper boundary disclosure changed")
    need("కలిపే సంఖ్యలు (addends)" in text and "మొత్తం (sum)" in text and "వచ్చే ఫలితం" in text, "Sum/addend glossary distinction changed")
    need("పూర్తయ్యాయని అనుకోకండి" in text and "adds no source exercise, score or module-completion claim" in text, "Completion boundary changed")
    need(not re.search(r"\d+\s*[+−×÷=]\s*\d+", text), "Bridge adds a worked numeric lesson")
    return {"bridge_ids": 6, "support_links": 7, "objective_links": 5, "bridge_exercises": 0, "bridge_equations": 0}


def validate_b020() -> dict[str, int | str]:
    source, metadata, module = source_baseline()
    catalog = catalog_baseline()
    target = localize_catalog(source, catalog)
    bridge = bridge_baseline()
    result: dict[str, int | str] = {
        "status": "PASS",
        **validate_module_graph(module),
        **validate_coverage(module, source, metadata),
        **validate_target(source, target, catalog),
        **validate_bridge(bridge),
    }
    result["source_sha256"] = sha((BASE / "sources/TE-B020.en.cnxml").read_bytes())
    result["catalog_sha256"] = sha((BASE / "translations/TE-B020.te.json").read_bytes())
    result["bridge_sha256"] = sha((BASE / "translations/TE-B020.bridge.xhtml").read_bytes())
    return result


if __name__ == "__main__":
    print(json.dumps(validate_b020(), ensure_ascii=False, indent=2))
