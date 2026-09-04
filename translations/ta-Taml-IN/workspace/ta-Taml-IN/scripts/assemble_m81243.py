"""Assemble checked Tamil m81243 source fragments, not a learner publication.

All validation happens before either output is written. Missing fragments,
changed pinned witnesses, structural/math drift, unresolved IDs, missing media,
or obvious unresolved-authoring markers fail closed. No answers are invented.
--check-only validates candidate inputs; it does not compare or certify any
previously written assembled-source or receipt bytes.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

LANG = Path(__file__).resolve().parents[1]
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
MD = "http://cnx.rice.edu/mdml"
SVG = "http://www.w3.org/2000/svg"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
LOCALE = "ta-Taml-IN"
ORDER = (
    "fs-id1830385", "fs-id2340048", "fs-id1883656", "fs-id1321580",
    "fs-id1339359", "fs-id2472737", "fs-id2296006", "fs-id2279009",
)
WITNESSES = {
    "en": (LANG / "provenance/m81243.en.cnxml", "396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b"),
    "id-ID": (LANG / "provenance/m81243.id-ID.cnxml", "7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251"),
}
FRONT = LANG / "translation/m81243-frontmatter.cnxml"
GLOSSARY = LANG / "translation/m81243-glossary.cnxml"
OUTPUT = LANG / "translation/m81243.cnxml"
RECEIPT = LANG / "qa/M81243-source-receipt.json"
UNRESOLVED = re.compile(r"\b(?:TODO|TBD|FIXME|TRANSLATE_ME|PLACEHOLDER)\b|\?\?\?", re.I)


class AssemblyError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AssemblyError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return path.relative_to(LANG).as_posix()


def parse_required(path):
    require(path.is_file(), f"Missing required fragment/input: {relative(path)}")
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise AssemblyError(f"Invalid XML: {relative(path)}: {exc}") from exc


def text(node):
    return "".join(node.itertext()).strip()


def stable_attributes(node):
    ignored = {XML_LANG}
    if node.tag == f"{{{C}}}media":
        ignored.add("alt")
    elif node.tag == f"{{{C}}}image":
        ignored.update(("src", "mime-type"))
    elif node.tag == f"{{{C}}}table":
        ignored.add("aria-label")
    return {key: value for key, value in node.attrib.items() if key not in ignored}


def math_signature(node):
    value = (node.text or "").strip()
    if node.tag == f"{{{M}}}mtext":
        # Only linguistic labels may differ; digits, punctuation, and operators
        # embedded in mtext must stay unchanged just like mathematical tokens.
        value = re.sub(r"[^0-9$€₹.,…+\-=/×÷%]", "", value)
    return node.tag, sorted(node.attrib.items()), value, [math_signature(child) for child in node]


def compare_source(source, target, label):
    src_nodes, dst_nodes = list(source.iter()), list(target.iter())
    require([n.tag for n in src_nodes] == [n.tag for n in dst_nodes], f"Source element hierarchy/order changed: {label}")
    require([len(n) for n in src_nodes] == [len(n) for n in dst_nodes], f"Source child counts/hierarchy changed: {label}")
    require([stable_attributes(n) for n in src_nodes] == [stable_attributes(n) for n in dst_nodes], f"Source IDs/non-language attributes changed: {label}")
    require([math_signature(n) for n in source.iter(f"{{{M}}}math")] == [math_signature(n) for n in target.iter(f"{{{M}}}math")], f"MathML drift: {label}")
    # Three dots and U+2026 are equivalent prose typography (U008's final
    # self-check prompt uses this change). MathML itself remains strict above.
    require(re.findall(r"[0-9]+|…", text(source).replace("...", "…")) == re.findall(r"[0-9]+|…", text(target).replace("...", "…")), f"Source prose/math numeral or ellipsis sequence changed: {label}")
    for src, dst in zip(src_nodes, dst_nodes):
        # Tamil can move prose before/after an unchanged inline MathML/link
        # child. Check direct prose collectively, not its language-specific
        # placement in node.text versus child.tail slots.
        src_prose = (src.text or "") + "".join(child.tail or "" for child in src)
        dst_prose = (dst.text or "") + "".join(child.tail or "" for child in dst)
        if src_prose.strip():
            require(dst_prose.strip(), f"Source direct text removed: {label}: {src.get('id', src.tag)}")


def check_authored(root, label):
    require(root.get(XML_LANG) == LOCALE, f"Missing or wrong fragment language: {label}")
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    require(len(ids) == len(set(ids)), f"Duplicate IDs in {label}")
    for node in root.iter():
        for value in [node.text or "", node.tail or "", *node.attrib.values()]:
            require(not UNRESOLVED.search(value), f"Unresolved authoring marker in {label}: {value[:100]}")


def solution_inventory(root):
    records = []
    content = root.find(f"{{{C}}}content")
    if content is None:
        return records
    for section in content:
        for exercise in section.iter(f"{{{C}}}exercise"):
            solutions = exercise.findall(f"{{{C}}}solution")
            empty = [s.get("id") for s in solutions if not text(s) and len(s) == 0]
            if not solutions or empty:
                records.append({
                    "section_id": section.get("id"),
                    "exercise_id": exercise.get("id"),
                    "problem_ids": [p.get("id") for p in exercise.findall(f"{{{C}}}problem")],
                    "status": "source-has-no-solution-node" if not solutions else "source-has-empty-solution-node",
                    "empty_solution_ids": empty,
                })
    return records


def validate_svg(asset):
    root = parse_required(asset)
    require(root.tag == f"{{{SVG}}}svg", f"Not an SVG document: {relative(asset)}")
    require(root.get("viewBox"), f"SVG has no viewBox: {relative(asset)}")
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    require(len(ids) == len(set(ids)), f"Duplicate local SVG IDs: {relative(asset)}")
    require(root.find(f"{{{SVG}}}title") is not None and text(root.find(f"{{{SVG}}}title")), f"SVG title missing: {relative(asset)}")
    require(root.find(f"{{{SVG}}}desc") is not None and text(root.find(f"{{{SVG}}}desc")), f"SVG description missing: {relative(asset)}")
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        require(local not in ("script", "foreignObject"), f"Active/unhandled SVG element: {relative(asset)}: {local}")
        for key, value in node.attrib.items():
            require(not key.rsplit("}", 1)[-1].lower().startswith("on"), f"Active SVG event-handler attribute: {relative(asset)}: {key}")
            if key.rsplit("}", 1)[-1] == "href":
                require(value.startswith("#") and value[1:] in ids, f"Unresolved/external SVG reference: {relative(asset)}: {value}")
            for reference in re.findall(r"url\(['\"]?([^)'\"]+)", value):
                require(reference.startswith("#") and reference[1:] in ids, f"Unresolved/external SVG URL: {relative(asset)}: {reference}")
        if local == "style":
            require("@import" not in text(node).lower() and not re.search(r"url\s*\(", text(node), re.I), f"External/unhandled SVG stylesheet dependency: {relative(asset)}")


def assemble():
    input_paths = [path for path, _ in WITNESSES.values()] + [FRONT, GLOSSARY] + [LANG / f"translation/m81243-{sid}.cnxml" for sid in ORDER]
    for path in input_paths:
        require(path.is_file(), f"Missing required fragment/input: {relative(path)}")
    input_snapshot = {path: sha(path) for path in input_paths}
    roots = {}
    for locale, (path, expected_sha) in WITNESSES.items():
        root = parse_required(path)
        require(sha(path) == expected_sha, f"Pinned source witness changed: {relative(path)}")
        require([n.tag for n in root] == [f"{{{C}}}{tag}" for tag in ("title", "metadata", "content", "glossary")], f"Unhandled module-level source material: {locale}")
        require(tuple(s.get("id") for s in root.find(f"{{{C}}}content")) == ORDER, f"Canonical section order changed: {locale}")
        roots[locale] = root

    front, glossary = parse_required(FRONT), parse_required(GLOSSARY)
    check_authored(front, relative(FRONT))
    check_authored(glossary, relative(GLOSSARY))
    require(front.tag == f"{{{C}}}document" and [n.tag for n in front] == [f"{{{C}}}title", f"{{{C}}}metadata"], "Front matter must be a document fragment with title+metadata only")
    require(glossary.tag == f"{{{C}}}glossary", "Wrong glossary fragment root")
    require(len(glossary.findall(f"{{{C}}}definition")) == 7, "Expected exactly seven source definitions")
    for locale, root in roots.items():
        expected_front = deepcopy(root)
        for child in list(expected_front)[2:]:
            expected_front.remove(child)
        compare_source(expected_front, front, f"front matter/{locale}")
        compare_source(root.find(f"{{{C}}}glossary"), glossary, f"glossary/{locale}")
        for tag in ("content-id", "uuid"):
            require(text(front.find(f"{{{C}}}metadata/{{{MD}}}{tag}")) == text(root.find(f"{{{C}}}metadata/{{{MD}}}{tag}")), f"Metadata identifier changed: {tag}")
    require(text(front.find(f"{{{C}}}title")) == text(front.find(f"{{{C}}}metadata/{{{MD}}}title")), "Root and metadata titles disagree")
    objectives = front.findall(f"{{{C}}}metadata/{{{MD}}}abstract/{{{C}}}list/{{{C}}}item")
    require(len(objectives) == 6 and all(text(item) for item in objectives), "Expected exactly six nonempty learning objectives")

    output = deepcopy(front)
    content = ET.Element(f"{{{C}}}content", dict(roots["en"].find(f"{{{C}}}content").attrib))
    fragments, source_sections = [], []
    for index, sid in enumerate(ORDER):
        path = LANG / f"translation/m81243-{sid}.cnxml"
        target = parse_required(path)
        check_authored(target, relative(path))
        require(target.tag == f"{{{C}}}section" and target.get("id") == sid, f"Wrong source section root: {relative(path)}")
        for locale, root in roots.items():
            source = root.find(f"{{{C}}}content/{{{C}}}section[@id='{sid}']")
            compare_source(source, target, f"{sid}/{locale}")
        if index < 6:
            require(text(objectives[index]) == text(target.find(f"{{{C}}}title")), f"Objective and section terminology disagree: {sid}")
        content.append(deepcopy(target))
        fragments.append({"path": relative(path), "sha256": sha(path), "source_id": sid})
        source_sections.append({
            "source_id": sid, "elements": len(list(target.iter())),
            "ids": sum(bool(n.get("id")) for n in target.iter()),
            "mathml": len(list(target.iter(f"{{{M}}}math"))),
            "exercises": len(list(target.iter(f"{{{C}}}exercise"))),
            "solutions": len(list(target.iter(f"{{{C}}}solution"))),
        })
    output.append(content)
    output.append(deepcopy(glossary))
    for locale, root in roots.items():
        compare_source(root, output, f"complete assembled source/{locale}")
        require(solution_inventory(root) == solution_inventory(output), f"Source missing-solution inventory changed: {locale}")

    ids = [n.get("id") for n in output.iter() if n.get("id")]
    require(len(ids) == len(set(ids)), "Duplicate IDs in assembled module")
    id_set, links, media, unique_assets = set(ids), [], [], {}
    for node in output.iter(f"{{{C}}}link"):
        target_id, url = node.get("target-id"), node.get("url")
        require(bool(target_id) != bool(url), f"Unhandled link form: {node.attrib}")
        if target_id:
            require(target_id in id_set, f"Unresolved source target: {target_id}")
            links.append({"target_id": target_id, "kind": "within-assembled-module"})
        else:
            parsed = urlparse(url)
            require(parsed.scheme in ("http", "https") and parsed.netloc, f"Unresolved external URL: {url}")
            links.append({"url": url, "kind": "source-external-link-not-offline-runtime-dependency"})
    for medium in output.iter(f"{{{C}}}media"):
        require((medium.get("alt") or "").strip(), f"Missing media text alternative: {medium.get('id')}")
        for image in medium.iter(f"{{{C}}}image"):
            src = image.get("src") or ""
            require(src and not urlparse(src).scheme, f"Unresolved/remote media: {src}")
            asset = (OUTPUT.parent / src).resolve()
            require(asset.is_relative_to((LANG / "assets").resolve()), f"Media escaped assets directory: {src}")
            require(asset.is_file(), f"Missing media: {relative(asset)}")
            require(image.get("mime-type") == "image/svg+xml" and asset.suffix.lower() == ".svg", f"Unreviewed media format: {relative(asset)}")
            if asset not in unique_assets:
                validate_svg(asset)
                unique_assets[asset] = sha(asset)
            media.append({"media_id": medium.get("id"), "path": relative(asset), "sha256": unique_assets[asset]})

    changes = []
    math_text_changes = []
    for index, (source, target) in enumerate(zip(roots["en"].iter(), output.iter())):
        changed = {key: {"source": source.get(key), "target": target.get(key)} for key in sorted(set(source.attrib) | set(target.attrib)) if source.get(key) != target.get(key)}
        if changed:
            changes.append({"element_index": index, "tag": target.tag.rsplit("}", 1)[-1], "id": target.get("id"), "changes": changed})
        if source.tag == f"{{{M}}}mtext" and (source.text or "").strip() != (target.text or "").strip():
            math_text_changes.append({"element_index": index, "source_en": source.text, "target_ta": target.text})

    ET.register_namespace("", C)
    ET.register_namespace("m", M)
    ET.register_namespace("md", MD)
    data = ET.tostring(output, encoding="utf-8", xml_declaration=True) + b"\n"
    # Reparse the exact bytes to be written; serialization must not lose nodes.
    for locale, source in roots.items():
        compare_source(source, ET.fromstring(data), f"serialized assembly/{locale}")
    for path, expected_sha in {**input_snapshot, **unique_assets}.items():
        require(path.is_file() and sha(path) == expected_sha, f"Input changed during assembly; rerun after it settles: {relative(path)}")
    missing_solutions = solution_inventory(output)
    receipt = {
        "schema_version": 1,
        "status": "source-module-assembled-structurally-verified-not-complete-learner-workflow",
        "module": "m81243", "locale": LOCALE,
        "all_canonical_source_nodes_included": True,
        "whole_assignment_complete": False, "learner_workflow_complete": False, "publication_ready": False,
        "witnesses": {relative(path): expected_sha for path, expected_sha in WITNESSES.values()},
        "assembler": {"path": relative(Path(__file__).resolve()), "sha256": sha(Path(__file__).resolve())},
        "front_matter": {"path": relative(FRONT), "sha256": sha(FRONT)},
        "sections_in_canonical_order": fragments,
        "glossary": {"path": relative(GLOSSARY), "sha256": sha(GLOSSARY)},
        "assembled_source": {"path": relative(OUTPUT), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()},
        "counts": {"sections": 8, "objectives": 6, "glossary_definitions": 7, "elements": len(list(output.iter())), "unique_ids": len(ids), "mathml": len(list(output.iter(f"{{{M}}}math"))), "exercises": len(list(output.iter(f"{{{C}}}exercise"))), "source_supplied_solutions": len(list(output.iter(f"{{{C}}}solution"))), "source_exercises_without_solutions": len(missing_solutions), "media_occurrences": len(media), "unique_svg_assets": len(unique_assets), "links": len(links)},
        "checks": {"both_witnesses_structure_and_stable_attributes": "pass", "both_witnesses_mathml_and_numeric_text_sequence": "pass", "all_source_ids_unique_and_preserved": "pass", "all_module_links_resolved": "pass", "all_media_local_present_and_svg_xml_checked": "pass", "source_solution_presence_unchanged": "pass", "serialized_output_reparsed": "pass"},
        "section_counts": source_sections,
        "documented_adaptations": {"translatable_prose": "Tamil replaces English/Indonesian prose, terms, titles, metadata abstract, and linguistic MathML mtext labels; mathematical token checks remain enforced. Prose may move around unchanged inline children for Tamil word order; three-dot and U+2026 prose ellipses are normalized as equivalent typography.", "attribute_changes": changes, "mathml_linguistic_label_changes": math_text_changes},
        "links": links, "media": media,
        "missing_solution_inventory": missing_solutions,
        "missing_solution_policy": "These source exercises lack solution nodes in both witnesses. They are preserved unchanged, not repaired or admitted as independently answerable assessments. Any new answers/reasoning belong in a separately marked companion.",
        "limits": [
            "This is complete source-node assembly for one A00 module, not completion of A00, A10, A20, AX-1, AX-3, or the Grades 2-8 recovery assignment.",
            "Structural and numeric checks do not constitute native-speaker review or verification of every translated number-word/prose meaning.",
            "No full-module reader, EPUB, PDF, learner routing, answer-complete companion, or assistive-technology/user validation is produced by this script.",
            "SVG local closure and XML checks do not substitute for source-figure visual/mathematical review.",
            "No external CNXML-schema validator or full-module rendered accessibility test is claimed by this source-tree check.",
            "External source hyperlinks are retained references, not packaged offline runtime dependencies.",
        ],
    }
    return data, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Validate candidate inputs without writing or verifying existing assembled-source/receipt bytes")
    args = parser.parse_args()
    try:
        data, receipt = assemble()
        if not args.check_only:
            require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024, "Less than 100 MiB free; refusing source assembly writes")
            OUTPUT.write_bytes(data)
            RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        summary = {"mode": "checked-only" if args.check_only else "assembled", "status": "candidate-inputs-validated-existing-output-not-verified" if args.check_only else receipt["status"], "candidate_source" if args.check_only else "output": receipt["assembled_source"], "counts": receipt["counts"]}
        if args.check_only:
            summary["existing_output_verified"] = False
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except (AssemblyError, OSError, ET.ParseError) as exc:
        print(f"ASSEMBLY FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
