"""Build the exact three-track complete m81268 CNXML draft."""
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET

from config import LANG
from safe_io import write_bytes
from use_algebra_common import (
    EN_SHA256,
    EXPECTED,
    ID_SHA256,
    MODULE,
    UNIT,
    build_variants,
    serialize,
    sha,
    source_counts,
    tree_sha,
)


def products() -> dict[str, bytes]:
    source, variants, edits, assets, indonesian_raw, english_raw = build_variants()
    generated = {
        f"translation/{UNIT}.id-academic.cnxml": indonesian_raw,
        f"translation/{UNIT}.jv-academic.cnxml": serialize(variants["jv-academic"]),
        f"translation/{UNIT}.jv-conversation.cnxml": serialize(variants["jv-conversation"]),
        f"provenance/{UNIT}.en.cnxml": english_raw,
    }
    for track in ("id-academic", "jv-academic", "jv-conversation"):
        root = ET.fromstring(generated[f"translation/{UNIT}.{track}.cnxml"])
        assert source_counts(root) == EXPECTED

    links = list(source.iter("{http://cnx.rice.edu/cnxml}link"))
    local = [node for node in links if node.get("target-id") and not node.get("document")]
    cross_document = [node for node in links if node.get("document")]
    external = [node for node in links if node.get("url")]
    assert len(local) == 7 and len(cross_document) == 4 and len(external) == 4
    ids = {node.get("id") for node in source.iter() if node.get("id")}
    assert all(node.get("target-id") in ids for node in local)
    assert [(node.get("document"), node.get("target-id")) for node in cross_document] == [
        ("m81244", "fs-id1348056"),
        ("m81255", "fs-id2218296"),
        ("m81256", "fs-id2597529"),
        ("m81243", None),
    ]
    assert [node.get("url") for node in external] == [
        "https://openstaxcollege.org/l/24orderoperate",
        "https://openstaxcollege.org/l/24orderbasic",
        "https://openstaxcollege.org/l/24Evalexpress",
        "https://openstaxcollege.org/l/24evalexpress3",
    ]
    spans = [
        (node.get("namest"), node.get("nameend"), node.get("morerows"))
        for node in source.iter("{http://cnx.rice.edu/cnxml}entry")
        if node.get("namest") or node.get("nameend") or node.get("morerows")
    ]
    assert spans == [("c1", "c2", None), ("c1", "c2", None), (None, None, "4")]

    receipt = {
        "schema": "jv-complete-module-draft-v1",
        "unit": UNIT,
        "module": MODULE,
        "status": "complete_source_bound_three_track_draft_production_audio_pending",
        "scope": (
            "Exact complete pinned m81268 document: title, metadata/four objectives, "
            "all ten sections, 107 exercises, all 71 supplied solutions, 36 source-absent "
            "solutions, 35 tables, 44 media, and two closing definitions."
        ),
        "source": {
            "indonesian_sha256": ID_SHA256,
            "english_sha256": EN_SHA256,
            "indonesian_bytes": len(indonesian_raw),
            "english_bytes": len(english_raw),
            "id_academic_is_exact_pinned_blob": generated[f"translation/{UNIT}.id-academic.cnxml"] == indonesian_raw,
            "english_witness_is_exact_pinned_blob": generated[f"provenance/{UNIT}.en.cnxml"] == english_raw,
        },
        "counts": EXPECTED,
        "source_tree_sha256": tree_sha(source),
        "target_tree_sha256": {track: tree_sha(root) for track, root in variants.items()},
        "translation_handoff_sha256": sha((LANG / f"translation/{UNIT}.edits.json").read_bytes()),
        "asset_manifest_sha256": sha((LANG / f"translation/{UNIT}.assets.json").read_bytes()),
        "source_phrase_bindings": len(edits["source_key_bindings"]),
        "scoped_accessibility_corrections": len(assets["scoped_accessibility_corrections"]),
        "links": {
            "local": len(local),
            "cross_document": len(cross_document),
            "external": len(external),
        },
        "table_spans": {
            "colspan_entries": 2,
            "rowspan_entries": 1,
            "exact_source_attributes": spans,
        },
        "checks": [
            "exact_pinned_source_blobs",
            "all_543_exact_phrase_bindings",
            "ordered_ids_and_complete_source_counts",
            "mathml_structure_attributes_and_non_mtext_tokens",
            "seven_element_slot_scoped_accessibility_repairs",
            "exact_manifest_integration_override_eip_id1164754514704",
            "local_cross_document_and_external_link_inventory",
            "real_thead_and_cals_span_inventory",
        ],
        "output_sha256": {path: sha(raw) for path, raw in generated.items()},
        "human_language_review": False,
        "integrated_visual_review": False,
        "screen_reader_review": False,
        "listening_review": False,
        "synthesized_audio_files": 0,
        "full_assignment_complete": False,
    }
    # The parent lane owns shared coverage integration.  Keep the coherent
    # receipt outside the globally inventoried *draft-receipt.json pattern
    # until that separate integration happens.
    generated[f"qa/{UNIT}.draft-receipt.in-progress.json"] = (
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    generated = products()
    assert generated == products(), "Nondeterministic m81268 drafting"
    for relative, raw in generated.items():
        path = LANG / relative
        if arguments.check:
            assert path.read_bytes() == raw, f"Stale m81268 draft: {relative}"
        else:
            write_bytes(path, raw)
    print(f"{UNIT}: complete three-track source-bound CNXML draft verified")


if __name__ == "__main__":
    main()
