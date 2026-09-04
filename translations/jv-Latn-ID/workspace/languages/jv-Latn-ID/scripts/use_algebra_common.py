"""Exact-source helpers for the complete A00 m81268 production package.

This module deliberately does not register m81268 in the shared unit builder.
The source, phrase ledger, accessibility exceptions, and asset manifest are
large complete-module inputs with their own fail-closed contracts.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from build import CN, MATH, XML_LANG, local
from config import DOWNLOADS, LANG, TRACKS

UNIT = "a00-use-algebra"
MODULE = "m81268"
ID_COMMIT = "3de9207f56f8b5c57c017abf973fb04e00d740f1"
EN_COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ID_PATH = "modules/m81268/index.cnxml"
EN_PATH = "modules/m81268/index.cnxml"
ID_SHA256 = "6fc5288d96f74128429a8bdcacb4cd94bb1a07182729dc23c30af37204a76222"
EN_SHA256 = "7a46eec9084976ca082e71f10f4cad97f2ba231d7b390e27753a21efb530bf87"
EDITS_SHA256 = "99a688f1eb0f696637ec91149ab25da06f6cbc0937addc0864092984f26e2121"
ASSETS_SHA256 = "aaac21e97f47600692f55ddde64cc7444881bb65bad083800751f6599213f232"
CANON_LOCK_SHA256 = "396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76"
OVERRIDE_ID = "eip-id1164754514704"
OVERRIDE_SLOT = "aria-label"
OVERRIDE_REQUIRED_FRAGMENT = "Apa ana eksponen? ora."

# The draft handoff is immutable, but four of its target spellings predate
# binding project-wide canon decisions.  These are finite, row-bound target
# integration revisions; the Indonesian source keys and edit ledger stay byte
# identical.  ``target_mentions`` counts live target occurrences, including
# repeated uses of the same exact source key.
CANON_TARGET_REVISIONS = (
    {
        "old": "gedhe", "new": "gedhé",
        "phrase_indices": (118, 119, 140, 145, 146, 148, 149, 151,
                           157, 162, 165, 169, 456, 476, 478, 479),
        "phrase_mentions": 19, "target_mentions": 24,
    },
    {
        "old": "seket", "new": "sèket",
        "phrase_indices": (230, 235),
        "phrase_mentions": 2, "target_mentions": 2,
    },
    {
        "old": "selawe", "new": "salawé",
        "phrase_indices": (366, 434),
        "phrase_mentions": 5, "target_mentions": 5,
    },
    {
        "old": "pitung likur", "new": "pitulikur",
        "phrase_indices": (98, 160, 434),
        "phrase_mentions": 5, "target_mentions": 5,
    },
)

EXPECTED = {
    "ids": 731,
    "mathml": 441,
    "sections": 10,
    "exercises": 107,
    "solutions": 71,
    "absent_solutions": 36,
    "tables": 35,
    "media": 44,
    "definitions": 2,
    "links": 15,
    "header_rows": 12,
    "header_cells": 30,
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(value) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode("utf-8"))


def pinned_blob(repository: str, commit: str, path: str) -> bytes:
    environment = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0")
    return subprocess.check_output(
        ["git", "-C", str(DOWNLOADS / repository), "show", f"{commit}:{path}"],
        env=environment,
    )


def source_blobs() -> tuple[bytes, bytes]:
    indonesian = pinned_blob("a00-id", ID_COMMIT, ID_PATH)
    english = pinned_blob("openstax-prealgebra-bundle", EN_COMMIT, EN_PATH)
    assert sha(indonesian) == ID_SHA256 and len(indonesian) == 153454
    assert sha(english) == EN_SHA256 and len(english) == 152620
    return indonesian, english


def load_contracts() -> tuple[dict, dict]:
    edits_raw = (LANG / f"translation/{UNIT}.edits.json").read_bytes()
    assets_raw = (LANG / f"translation/{UNIT}.assets.json").read_bytes()
    assert sha(edits_raw) == EDITS_SHA256, "Changed immutable m81268 edit ledger"
    assert sha(assets_raw) == ASSETS_SHA256, "Changed reviewed m81268 asset manifest"
    edits = json.loads(edits_raw)
    assets = json.loads(assets_raw)
    assert edits["unit"] == assets["unit"] == UNIT
    assert edits["source_module"] == assets["module"] == MODULE
    assert edits["tracks"] == ["jv-academic", "jv-conversation"]
    assert len(edits["phrases"]) == len(edits["source_key_bindings"]) == 543
    assert len(assets["assets"]) == 44
    return edits, assets


def tree_key(element: ET.Element) -> str:
    element = copy.deepcopy(element)
    element.tail = None
    return ET.canonicalize(
        ET.tostring(element, encoding="unicode"),
        strip_text=True,
        rewrite_prefixes=True,
    )


def tree_sha(element: ET.Element) -> str:
    return sha(tree_key(element).encode("utf-8"))


def manifest_c14n(element: ET.Element) -> str:
    """Reproduce the asset manifest's whitespace-preserving element binding."""
    return ET.canonicalize(
        ET.tostring(element, encoding="unicode"),
        strip_text=False,
        rewrite_prefixes=True,
    )


def nodes_by_id(root: ET.Element) -> dict[str, ET.Element]:
    result = {node.get("id"): node for node in root.iter() if node.get("id")}
    assert len(result) == EXPECTED["ids"]
    return result


def source_counts(root: ET.Element) -> dict[str, int]:
    exercises = list(root.iter("{" + CN + "}exercise"))
    solutions = list(root.iter("{" + CN + "}solution"))
    tables = list(root.iter("{" + CN + "}table"))
    header_rows = [row for table in tables for row in table.findall(".//{*}thead/{*}row")]
    header_cells = [cell for row in header_rows for cell in row.findall("{*}entry")]
    counts = {
        "ids": len([node for node in root.iter() if node.get("id")]),
        "mathml": len(list(root.iter("{" + MATH + "}math"))),
        "sections": len(list(root.iter("{" + CN + "}section"))),
        "exercises": len(exercises),
        "solutions": len(solutions),
        "absent_solutions": sum(
            exercise.find("{" + CN + "}solution") is None for exercise in exercises
        ),
        "tables": len(tables),
        "media": len(list(root.iter("{" + CN + "}media"))),
        "definitions": len(list(root.iter("{" + CN + "}definition"))),
        "links": len(list(root.iter("{" + CN + "}link"))),
        "header_rows": len(header_rows),
        "header_cells": len(header_cells),
    }
    assert counts == EXPECTED, counts
    return counts


def _parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}


def _nearest_id(node: ET.Element, parents: dict[ET.Element, ET.Element]) -> str:
    while node is not None:
        if node.get("id"):
            return node.get("id")
        node = parents.get(node)
    return ""


def validate_phrase_bindings(source: ET.Element, edits: dict) -> None:
    """Bind every unique phrase to its recorded exact element/slot/anchor."""
    parents = _parent_map(source)
    phrase_rows = edits["phrases"]
    indices = [row["phrase_index_zero_based"] for row in edits["source_key_bindings"]]
    assert indices == list(range(len(phrase_rows)))
    for binding in edits["source_key_bindings"]:
        index = binding["phrase_index_zero_based"]
        key = phrase_rows[index][0]
        candidates = []
        for node in source.iter():
            if local(node) != binding["element"]:
                continue
            slot = binding["slot"]
            value = node.text if slot == "text" else node.tail if slot == "tail" else node.get(slot)
            if value is None or value.strip() != key.strip():
                continue
            anchor_node = parents.get(node) if slot == "tail" else node
            if _nearest_id(anchor_node, parents) != binding["element_id"]:
                continue
            candidates.append(node)
        # A binding identifies the exact source key and its recorded anchor;
        # the same key may deliberately occur more than once at that anchor
        # (the document title is also repeated in metadata).  Translation is
        # still key-exact and the ledger itself contains no duplicate key.
        assert candidates, (
            f"Phrase binding {index} did not resolve: "
            f"{binding['element_id']} {binding['element']}@{binding['slot']}"
        )


def translate_full_source(source: ET.Element, track: str, edits: dict) -> ET.Element:
    """Replay the worker's whitespace-significant exact phrase ledger.

    The shared pilot translator keys on stripped strings.  This complete-module
    ledger intentionally includes several leading/trailing spaces as part of
    the reviewed source slot, so its replay is necessarily unit-local.
    """
    index = edits["tracks"].index(track) + 1
    exact = {row[0]: row[index] for row in edits["phrases"]}
    unchanged = set(edits["unchanged_identifiers"])

    def replace(value: str | None) -> str | None:
        if value is None or not value.strip():
            return value
        if value in exact:
            return exact[value]
        key = value.strip()
        if value in unchanged or key in unchanged or not re.search("[A-Za-z]", key):
            return value
        raise ValueError(f"Untranslated exact m81268 source slot: {value!r}")

    target = copy.deepcopy(source)
    exact_math_identifiers = {"a", "b", "c", "g", "h", "m", "n", "p", "q", "t", "x", "y"}
    for node in target.iter():
        if node.tag == "{" + MATH + "}mi" and (node.text or "") in exact_math_identifiers:
            pass
        else:
            node.text = replace(node.text)
        node.tail = replace(node.tail)
        for attribute in ("alt", "aria-label", "summary"):
            if attribute in node.attrib:
                node.set(attribute, replace(node.get(attribute)))
    target.set(XML_LANG, "jv-Latn-ID")
    return target


def apply_canon_target_revisions(target: ET.Element, track: str, edits: dict) -> None:
    """Apply the finite reviewed spellings without mutating the edit ledger."""
    track_index = edits["tracks"].index(track) + 1
    phrase_outputs = [row[track_index] for row in edits["phrases"]]
    revisions: dict[str, str] = {}
    for spec in CANON_TARGET_REVISIONS:
        actual_indices = tuple(
            index for index, value in enumerate(phrase_outputs)
            if spec["old"] in value
        )
        assert actual_indices == spec["phrase_indices"]
        assert sum(phrase_outputs[index].count(spec["old"])
                   for index in actual_indices) == spec["phrase_mentions"]
        for index in actual_indices:
            old_value = phrase_outputs[index]
            new_value = old_value.replace(spec["old"], spec["new"])
            if old_value in revisions:
                assert revisions[old_value] == new_value or spec["old"] in revisions[old_value]
                revisions[old_value] = revisions[old_value].replace(spec["old"], spec["new"])
            else:
                revisions[old_value] = new_value

    before = {spec["old"]: 0 for spec in CANON_TARGET_REVISIONS}
    slots: list[tuple[ET.Element, str]] = []
    for node in target.iter():
        slots.extend((node, slot) for slot in ("text", "tail")
                     if getattr(node, slot) is not None)
        slots.extend((node, slot) for slot in ("alt", "aria-label", "summary")
                     if node.get(slot) is not None)
    for node, slot in slots:
        value = getattr(node, slot) if slot in ("text", "tail") else node.get(slot)
        for spec in CANON_TARGET_REVISIONS:
            before[spec["old"]] += value.count(spec["old"])
        if value in revisions:
            value = revisions[value]
            if slot in ("text", "tail"):
                setattr(node, slot, value)
            else:
                node.set(slot, value)
    assert before == {
        spec["old"]: spec["target_mentions"] for spec in CANON_TARGET_REVISIONS
    }, before
    for node, slot in slots:
        value = getattr(node, slot) if slot in ("text", "tail") else node.get(slot)
        assert all(spec["old"] not in value for spec in CANON_TARGET_REVISIONS)


def _apply_accessibility_override(target: ET.Element, track: str, assets: dict) -> None:
    corrections = assets["scoped_accessibility_corrections"]
    override = next(
        row for row in corrections
        if row["element_id"] == OVERRIDE_ID and row["slot"] == OVERRIDE_SLOT
    )
    node = nodes_by_id(target)[OVERRIDE_ID]
    expected = override["target_surfaces"][track]
    assert OVERRIDE_REQUIRED_FRAGMENT in expected
    assert OVERRIDE_REQUIRED_FRAGMENT not in node.get(OVERRIDE_SLOT)
    node.set(OVERRIDE_SLOT, expected)


def build_variants() -> tuple[ET.Element, dict[str, ET.Element], dict, dict, bytes, bytes]:
    indonesian_raw, english_raw = source_blobs()
    edits, assets = load_contracts()
    source = ET.fromstring(indonesian_raw)
    english = ET.fromstring(english_raw)
    source_counts(source)
    assert source_counts(english) == EXPECTED
    validate_phrase_bindings(source, edits)
    variants = {"id-academic": copy.deepcopy(source)}
    for track in ("jv-academic", "jv-conversation"):
        target = translate_full_source(source, track, edits)
        apply_canon_target_revisions(target, track, edits)
        _apply_accessibility_override(target, track, assets)
        variants[track] = target
    validate_variants(source, variants, edits, assets)
    return source, variants, edits, assets, indonesian_raw, english_raw


def validate_variants(source: ET.Element, variants: dict[str, ET.Element],
                      edits: dict, assets: dict) -> None:
    source_ids = [node.get("id") for node in source.iter() if node.get("id")]
    assert len(source_ids) == len(set(source_ids)) == EXPECTED["ids"]
    source_math = list(source.iter("{" + MATH + "}math"))
    corrections = {
        (row["element_id"], row["slot"]): row
        for row in assets["scoped_accessibility_corrections"]
    }
    assert len(corrections) == 7
    source_nodes = nodes_by_id(source)
    for row in corrections.values():
        node = source_nodes[row["element_id"]]
        assert node.get(row["slot"]) == row["old_source_surface"]
        assert sha(row["old_source_surface"].encode("utf-8")) == row["old_source_surface_sha256"]
        element_c14n = manifest_c14n(node)
        assert element_c14n == row["source_element_c14n"]
        assert sha(element_c14n.encode("utf-8")) == row["source_element_c14n_sha256"]
        assert row["source_module_sha256"] == ID_SHA256
        assert row["scope_hash"] == row["source_element_c14n_sha256"] or row["scope_hash"] == row.get("asset_sha256")
    for track, target in variants.items():
        target_ids = [node.get("id") for node in target.iter() if node.get("id")]
        assert target_ids == source_ids
        assert source_counts(target) == EXPECTED
        if track.startswith("jv"):
            assert target.get(XML_LANG) == "jv-Latn-ID"
        target_math = list(target.iter("{" + MATH + "}math"))
        assert len(target_math) == len(source_math) == EXPECTED["mathml"]
        for left, right in zip(source_math, target_math):
            for a, b in zip(left.iter(), right.iter()):
                assert a.tag == b.tag and a.attrib == b.attrib
                if local(a) != "mtext":
                    assert a.text == b.text
        if track == "id-academic":
            assert tree_key(target) == tree_key(source)
            continue
        replay = translate_full_source(source, track, edits)
        apply_canon_target_revisions(replay, track, edits)
        _apply_accessibility_override(replay, track, assets)
        assert tree_key(target) == tree_key(replay)
        target_nodes = nodes_by_id(target)
        for key, correction in corrections.items():
            assert target_nodes[key[0]].get(key[1]) == correction["target_surfaces"][track]
        assert OVERRIDE_REQUIRED_FRAGMENT in target_nodes[OVERRIDE_ID].get(OVERRIDE_SLOT)


def asset_maps(variants: dict[str, ET.Element], assets: dict) -> dict[str, dict[str, dict]]:
    rows = assets["assets"]
    assert [row["ordinal"] for row in rows] == list(range(1, 45))
    refs = [row["source"]["ref"] for row in rows]
    assert len(refs) == len(set(refs)) == EXPECTED["media"]
    source_media = list(variants["id-academic"].iter("{" + CN + "}media"))
    assert [node.get("id") for node in source_media] == [row["media_id"] for row in rows]
    assert [node.find("{*}image").get("src") for node in source_media] == refs
    result = {}
    for track in TRACKS:
        mapping = {}
        track_media = list(variants[track].iter("{" + CN + "}media"))
        for node, row in zip(track_media, rows):
            assert node.get("id") == row["media_id"]
            assert node.get("alt") == row["target_alt"][track]
            output = row["outputs"][track]
            path = LANG / output["path"]
            raw = path.read_bytes()
            assert sha(raw) == output["sha256"] and len(raw) == output["bytes"]
            assert path.name and output["mime_type"].startswith("image/")
            mapping[row["source"]["ref"]] = {
                "bytes": raw,
                "mime_type": output["mime_type"],
                "sha256": output["sha256"],
                "path": output["path"],
            }
        result[track] = mapping
    return result


def serialize(element: ET.Element) -> bytes:
    return ET.tostring(element, encoding="utf-8", xml_declaration=True) + b"\n"


def owned_path(relative: str) -> Path:
    assert Path(relative).name.startswith(UNIT) or Path(relative).name.startswith("use_algebra")
    return LANG / relative
