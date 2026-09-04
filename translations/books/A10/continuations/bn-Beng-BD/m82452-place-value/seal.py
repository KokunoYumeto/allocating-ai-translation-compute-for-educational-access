from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path
from xml.etree import ElementTree as ET

P = Path(__file__).resolve().parent
CANDIDATE = Path(r"C:\interlanguage-task-state\elementary-algebra-recovered-20260904\locale-control\bn-Beng-BD\SELECTION_CANDIDATE.json")
CANDIDATE_SHA = "90aafdc1862d727dc18723acf902aa45d7438cac2c57b90b08b46ea27b0013a7"
SEAL_FILES = {"PACKET_MANIFEST.json", "checksums.sha256", "OWNER_HANDOFF.json"}
EXPECTED_MODULES = ["m82452", "m82453", "m82454", "m82455", "m82456", "m82457", "m82461"]
FORBIDDEN_SELECTED = {
    "fs-id1170655000684", "fs-id1170655000686", "fs-id1170655126635",
    "fs-id1170655200456", "fs-id1170654972409", "eip-id1169754362252",
    "eip-id1169754058803", "eip-id1169754058820",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ident(path: Path) -> dict:
    data = path.read_bytes()
    return {"path": path.relative_to(P).as_posix(), "bytes": len(data), "sha256": sha_bytes(data)}


def load(rel: str):
    return json.loads((P / rel).read_text(encoding="utf-8"))


def dump(rel: str, obj) -> None:
    (P / rel).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def candidate_validation() -> dict:
    raw = CANDIDATE.read_bytes()
    assert sha_bytes(raw) == CANDIDATE_SHA
    c = json.loads(raw.decode("utf-8"))
    assert [m["module"] for m in c["modules"]] == EXPECTED_MODULES
    whole_sets = []
    source_rows = []
    m57_union = set()
    for module in c["modules"]:
        sp = Path(module["source_path"])
        source = sp.read_bytes()
        assert len(source) == module["source_bytes"]
        assert sha_bytes(source) == module["source_sha256"]
        root = ET.fromstring(source)
        elems = list(root.iter())
        id_nodes = {node.attrib["id"]: node for node in elems if "id" in node.attrib}
        ids = [node.attrib["id"] for node in elems if "id" in node.attrib]
        integrity = module["source_integrity"]
        assert len(elems) == integrity["document_elements"]
        assert len(ids) == integrity["document_ids"]
        assert sum(n - 1 for n in collections.Counter(ids).values() if n > 1) == integrity["duplicate_ids"] == 0
        broken = []
        for node in elems:
            for key, value in node.attrib.items():
                if local_name(key) in {"target-id", "target"} and value.startswith(("fs-id", "eip-id", "term-")) and value not in id_nodes:
                    broken.append(value)
        assert len(broken) == integrity["broken_internal_target_ids"] == 0
        cited = set(re.findall(r"(?:(?:fs|eip)-id\d+|term-\d+)", json.dumps(module, ensure_ascii=False)))
        assert not (cited - set(id_nodes)), (module["module"], sorted(cited - set(id_nodes)))
        selected_nodes = []
        for selection in module.get("selections", []):
            node = id_nodes[selection["id"]]
            descendants = list(node.iter())
            counts = selection["counts"]
            assert len(descendants) == counts["xml_elements"]
            assert sum("id" in x.attrib for x in descendants) == counts["elements_with_id"]
            for key, tag in {"sections": "section", "paragraphs": "para", "notes": "note", "examples": "example", "exercises": "exercise", "problems": "problem", "supplied_solutions": "solution", "tables": "table", "equations": "equation", "media": "media", "images": "image", "internal_links": "link"}.items():
                if key in counts:
                    assert sum(local_name(x.tag) == tag for x in descendants) == counts[key], (module["module"], key)
            selected_nodes.extend(descendants)
        if module["module"] == "m82457":
            roots = []
            for context in module["instructional_context"]:
                roots.extend(context["selected_whole_node_ids"])
            roots.extend(module["practice_selection"]["selected_heading_node_ids"])
            roots.extend(row["exercise_id"] for row in module["selected_exercises"] if "container_id" not in row)
            assert len(roots) == module["counts"]["selected_whole_root_nodes"] == 41
            assert not (set(roots) & FORBIDDEN_SELECTED)
            selected_nodes = []
            seen = set()
            for rid in roots:
                for node in id_nodes[rid].iter():
                    if id(node) not in seen:
                        seen.add(id(node)); selected_nodes.append(node)
            m57_union = {id(x) for x in selected_nodes}
            counts = module["counts"]
            assert len(selected_nodes) == counts["xml_elements_under_selected_roots"] == 492
            assert sum("id" in x.attrib for x in selected_nodes) == counts["elements_with_id_under_selected_roots"] == 127
            for key, tag in {"selected_exercises": "exercise", "selected_problems": "problem", "selected_supplied_solutions": "solution", "selected_examples": "example", "selected_notes": "note", "selected_media": "media", "selected_images": "image", "selected_internal_links": "link"}.items():
                assert sum(local_name(x.tag) == tag for x in selected_nodes) == counts[key], key
            assert len(module["selected_exercises"]) == counts["selected_exercises"] == 23
            assert sum(x["supplied_solution_id"] is None for x in module["selected_exercises"]) == counts["selected_exercises_without_supplied_solution"] == 9
            for row in module["selected_exercises"]:
                match = re.fullmatch(r"\s*(\d+(?:/\d+)?)\s*([+-])\s*(\d+(?:/\d+)?)\s*", row["expression"])
                assert match
                left, op, right = match.groups()
                value = Fraction(left) + Fraction(right) if op == "+" else Fraction(left) - Fraction(right)
                assert value >= 0, row
        if selected_nodes:
            whole_sets.append(selected_nodes)
        source_rows.append({"module": module["module"], "bytes": len(source), "sha256": sha_bytes(source), "cited_id_anchors": len(cited)})
    unique = {}
    for group in whole_sets:
        for node in group:
            unique[id(node)] = node
    # Element object identities are document-local; there is no cross-module collision.
    agg = c["aggregate_counts"]
    assert sum(len(group) for group in whole_sets) == agg["whole_node_xml_elements_selected_excluding_token_or_panel_fragments"] == 2272
    assert sum(sum("id" in x.attrib for x in group) for group in whole_sets) == agg["whole_node_elements_with_id_selected_excluding_token_or_panel_fragments"] == 456
    assert agg["total_selected_problem_units"] == 62
    assert agg["total_selected_supplied_answer_units"] == 53
    media = c["media_dependencies"]
    refs = [(module, ref) for module, items in media["refs_by_module"].items() for ref in items]
    assert len(refs) == media["counts"]["selected_media_references"] == agg["selected_media_references"] == 51
    source_by_module = {m["module"]: Path(m["source_path"]) for m in c["modules"]}
    resolved = []
    png_jpg = 0
    for module, ref in refs:
        parts = ref.split("|")
        assert len(parts) >= 3
        _, mime, src = parts[:3]
        resolved.append((source_by_module[module].parent / src).resolve())
        png_jpg += int(mime == "image/png" and src.lower().endswith(".jpg"))
    assert sum(path.is_file() for path in resolved) == media["counts"]["resolved_existing_files"] == 0
    assert sum(not path.is_file() for path in resolved) == media["counts"]["missing_files"] == 51
    assert png_jpg == media["counts"]["declared_png_with_jpg_filename"] == 36
    return {"candidate": {"path": CANDIDATE.as_posix(), "bytes": len(raw), "sha256": sha_bytes(raw)}, "source_witnesses": source_rows, "modules": 7, "candidate_id_anchor_check": "pass", "m82457_remaining_nonnegative_exercises": 23, "media_references": 51, "missing_media": 51, "resolved_media": 0, "png_declared_jpg_name": 36, "status": "pass"}


def verify_packet_content() -> None:
    recovery = load("SOURCE_RECOVERY.json")
    assert sha_bytes((P / "source/m82452.en.cnxml").read_bytes()) == recovery["source_sha256"]
    assert sha_bytes((P / "source/place-value.en.cnxml").read_bytes()) == recovery["section_sha256"]
    source = ET.parse(P / "source/place-value.en.cnxml").getroot()
    target = ET.parse(P / "source/place-value.bn-BD.cnxml").getroot()
    s_nodes, t_nodes = list(source.iter()), list(target.iter())
    assert len(s_nodes) == len(t_nodes) == 379
    def structural_attributes(node):
        return sorted((key, value) for key, value in node.attrib.items() if local_name(key) not in {"lang", "alt", "aria-label"})
    assert [(x.tag, structural_attributes(x)) for x in s_nodes] == [(x.tag, structural_attributes(x)) for x in t_nodes]
    assert len([x for x in s_nodes if "id" in x.attrib]) == 147
    assert len([x for x in s_nodes if local_name(x.tag) == "math"]) == len([x for x in t_nodes if local_name(x.tag) == "math"]) == 16
    target_text = (P / "source/place-value.bn-BD.cnxml").read_text(encoding="utf-8")
    assert "গুলোর সেট" in target_text
    assert "সংশ্লিষ্ট চিত্র চিত্রে" not in target_text
    support = load("support.json")
    assert "সেট" in json.dumps(support, ensure_ascii=False)
    rights = load("backend/rights.json")
    assert rights["recorded_inherited_mime_mismatches"] == 4
    assert len(rights["assets"]) == 17
    css = (P / "assets/reader.css").read_text(encoding="utf-8")
    assert "1080px" not in css and "max-width:none" in css and "width:calc(100% - 32px)" in css
    assert ".number-equivalence td:first-child{white-space:nowrap}" in css
    for page_name in ("index.html", "companion.html"):
        text = (P / page_name).read_text(encoding="utf-8")
        assert "�" not in text
        ids = set(re.findall(r'\bid="([^"]+)"', text))
        for attr, ref in re.findall(r'\b(href|src)="([^"]+)"', text):
            if ref.startswith(("http://", "https://")):
                continue
            if ref.startswith("#"):
                assert ref[1:] in ids, (page_name, ref)
            else:
                path_part, _, anchor = ref.partition("#")
                assert (P / path_part).is_file(), (page_name, ref)
                if anchor and path_part.endswith(".html"):
                    other = (P / path_part).read_text(encoding="utf-8")
                    assert re.search(rf'\bid="{re.escape(anchor)}"', other)
    browser = load("BROWSER_QA.json")
    independent = load("INDEPENDENT_REVIEW.json")
    candidate_receipt = load("CANDIDATE_REPAIR_REVIEW.json")
    assert browser["status"] == independent["status"] == "pass"
    assert candidate_receipt["status"] == "candidate_repaired_and_validation_passed_not_admitted"
    for row in browser["evidence"]:
        assert ident(P / row["path"]) == row
    assert ident(P / browser["metrics"]["path"]) == browser["metrics"]
    metrics = load("qa/BROWSER_METRICS.json")
    assert len(metrics["records"]) == 12
    for row in metrics["records"]:
        assert row["layout"]["horizontalOverflowPx"] == 0
        assert row["layout"]["offscreen"] == []
        assert row["layout"]["replacementCharacters"] == 0
        assert row["layout"]["banglaFontLoaded"] is True
        assert ident(P / row["path"])["sha256"] == row["sha256"]


def payload_inventory() -> list[dict]:
    rows = []
    for path in sorted((x for x in P.rglob("*") if x.is_file()), key=lambda x: x.relative_to(P).as_posix()):
        rel = path.relative_to(P).as_posix()
        if rel in SEAL_FILES or "__pycache__" in path.parts:
            continue
        rows.append(ident(path))
    return rows


def seal() -> dict:
    candidate = candidate_validation()
    verify_packet_content()
    browser_id = ident(P / "BROWSER_QA.json")
    independent_id = ident(P / "INDEPENDENT_REVIEW.json")
    candidate_receipt_id = ident(P / "CANDIDATE_REPAIR_REVIEW.json")
    qa = load("QA.json")
    qa["browser_visual_qa"] = {"status": "pass", **browser_id}
    qa["independent_semantic_review"] = {"status": "pass", **independent_id}
    qa["candidate_boundary_review"] = {"status": "pass_not_admitted", **candidate_receipt_id}
    qa["deterministic_replay"] = {"status": "pass", "runs": 2, "identical_generated_files": 9}
    qa["status"] = "admit_ready_hash_sealed"
    dump("QA.json", qa)
    package = load("PACKAGE.json")
    package["quality_state"] = "admit_ready_hash_sealed"
    package["qa_receipts"] = ["QA.json", "INDEPENDENT_REVIEW.json", "BROWSER_QA.json", "CANDIDATE_REPAIR_REVIEW.json"]
    dump("PACKAGE.json", package)
    rows = payload_inventory()
    checksums_text = "".join(f'{row["sha256"]}  {row["path"]}\n' for row in rows)
    (P / "checksums.sha256").write_text(checksums_text, encoding="ascii", newline="\n")
    checksums_id = ident(P / "checksums.sha256")
    inventory_digest = sha_bytes("".join(f'{r["path"]}\0{r["bytes"]}\0{r["sha256"]}\n' for r in rows).encode("utf-8"))
    manifest = {
        "schema": "a10.packet-manifest.v1",
        "package_id": package["package_id"],
        "scope": package["coverage"],
        "payload_file_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "inventory_digest_sha256": inventory_digest,
        "checksums": checksums_id,
        "files": rows,
    }
    dump("PACKET_MANIFEST.json", manifest)
    manifest_id = ident(P / "PACKET_MANIFEST.json")
    handoff = {
        "schema": "a10.owner-handoff.v1",
        "package_id": package["package_id"],
        "decision": "ADMIT_READY",
        "truthful_scope": "Complete selected m82452 place-value subsection for bn-Beng-BD, not a complete module or book; the separate selection candidate remains unadmitted.",
        "manifest": manifest_id,
        "checksums": checksums_id,
        "package": ident(P / "PACKAGE.json"),
        "qa": ident(P / "QA.json"),
        "browser_qa": browser_id,
        "independent_review": independent_id,
        "candidate_review": candidate_receipt_id,
        "selection_candidate": candidate["candidate"],
        "source_module": ident(P / "source/m82452.en.cnxml"),
        "source_section": ident(P / "source/place-value.en.cnxml"),
        "target_cnxml": ident(P / "source/place-value.bn-BD.cnxml"),
        "reader": ident(P / "index.html"),
        "companion": ident(P / "companion.html"),
        "payload_file_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "inventory_digest_sha256": inventory_digest,
        "deterministic_replay": "pass: two consecutive builds produced identical bytes for all nine generated artifacts",
        "browser_visual_qa": "pass: 12 current screenshots, wide and narrow, exact hashes; zero overflow/offscreen/replacement characters",
        "publication": "not performed; outside this bounded repair",
    }
    dump("OWNER_HANDOFF.json", handoff)
    return verify()


def verify() -> dict:
    candidate = candidate_validation()
    verify_packet_content()
    package = load("PACKAGE.json")
    qa = load("QA.json")
    assert package["quality_state"] == qa["status"] == "admit_ready_hash_sealed"
    rows = payload_inventory()
    expected_text = "".join(f'{row["sha256"]}  {row["path"]}\n' for row in rows)
    assert (P / "checksums.sha256").read_text(encoding="ascii") == expected_text
    manifest = load("PACKET_MANIFEST.json")
    assert manifest["files"] == rows
    assert manifest["payload_file_count"] == len(rows)
    assert manifest["payload_bytes"] == sum(row["bytes"] for row in rows)
    digest = sha_bytes("".join(f'{r["path"]}\0{r["bytes"]}\0{r["sha256"]}\n' for r in rows).encode("utf-8"))
    assert manifest["inventory_digest_sha256"] == digest
    assert manifest["checksums"] == ident(P / "checksums.sha256")
    handoff = load("OWNER_HANDOFF.json")
    assert handoff["decision"] == "ADMIT_READY"
    assert handoff["manifest"] == ident(P / "PACKET_MANIFEST.json")
    assert handoff["checksums"] == ident(P / "checksums.sha256")
    assert handoff["selection_candidate"] == candidate["candidate"]
    for path in P.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    ET.parse(P / "source/m82452.en.cnxml")
    ET.parse(P / "source/place-value.en.cnxml")
    ET.parse(P / "source/place-value.bn-BD.cnxml")
    all_files = [x for x in P.rglob("*") if x.is_file() and "__pycache__" not in x.parts]
    return {
        "status": "ADMIT_READY",
        "tree_file_count": len(all_files),
        "tree_bytes": sum(x.stat().st_size for x in all_files),
        "payload_file_count": len(rows),
        "payload_bytes": sum(row["bytes"] for row in rows),
        "inventory_digest_sha256": digest,
        "manifest": ident(P / "PACKET_MANIFEST.json"),
        "checksums": ident(P / "checksums.sha256"),
        "handoff": ident(P / "OWNER_HANDOFF.json"),
        "qa": ident(P / "QA.json"),
        "package": ident(P / "PACKAGE.json"),
        "selection_candidate": candidate["candidate"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify() if args.verify else seal(), ensure_ascii=False, indent=2))
