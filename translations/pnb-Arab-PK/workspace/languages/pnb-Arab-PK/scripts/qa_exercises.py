"""Independent source-derived PNB-009 checks; mutations use detached DOMs only.

The renderer is deliberately not imported. Source MathML, hierarchy, block
ownership, table values, image bytes and answer pairing are derived independently.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import copy
import csv
import hashlib
import html
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from qa_notation import MATH, LEDGER, FORBIDDEN, paths, at_path, signature, unique_object, jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
READER = BASE / "reader/unit-009.html"
SECTION = "fs-id1165137737761"
TABLES = ["fs-id1165137644806", "fs-id1165137771744", "fs-id1165137758645", "fs-id1165137727218"]
# Independent audit of the actual terminal source leaves, not renderer ledgers.
NUMERIC_EDGES = {
    ("fs-id1165135195670", 1): "0.", ("fs-id1165135639752/item/2", 0): "7.",
    ("fs-id1165132950022/item/2", 0): "1.", ("fs-id1165137803284/item/2", 0): "2.",
    ("fs-id1165135320063/item/2", 0): "4.", ("fs-id1165137731069/item/2", 0): "4.",
    ("fs-id1165137433547", 0): "18.", ("fs-id1165135349856/item/3", 0): "2.",
    ("fs-id1165134054032/item/2", 0): "3.", ("fs-id1165137861994/item/2", 0): "−3.",
    ("fs-id1165134325875/item/2", 0): "1.", ("fs-id1165137723310", 0): "1.",
    ("fs-id1165135380706/item/2", 0): "2.", ("fs-id1165137834372/item/2", 0): "1.",
}
RECEIPTS = ["PNB-009-next-unit-20260831T023538508355Z.json", "PNB-009-draft-20260831T024400416135Z.json",
            "PNB-009-revision-20260831T025609340901Z.json", "PNB-009-qa-20260831T025851185845Z.json"]


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def text(node):
    return "".join(node.itertext()).strip()


def compact(value):
    return re.sub(r"\s+", "", value)


def sha256(path):
    raw = path.read_bytes()
    if path.suffix == ".cnxml":
        raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


def parents(node):
    return {child: owner for owner in node.iter() for child in owner}


def by_id(root, identifier):
    found = [n for n in root.iter() if n.get("id") == identifier]
    require("unique_id:" + identifier, len(found) == 1)
    return found[0]


def marked(root, attr, value):
    found = [n for n in root.iter() if n.get(attr) == value]
    require("unique_marker:" + value, len(found) == 1)
    return found[0]


def parse_reader(raw):
    return ET.fromstring(raw[raw.index("<html"):])


def validate_envelope(raw, check=require):
    check("exact_reader_envelope", raw.startswith('<!doctype html>\n<html lang="pnb-Arab-PK" dir="rtl">')
          and raw.endswith('</body></html>\n') and raw.count('<!doctype') == 1)


def pure(node):
    return node.text in (None, "") and all(c.tail in (None, "") for c in node)


def content_signature(node):
    return node.text, tuple((signature(c), c.tail) for c in node)


def retained_attrs(node):
    return {"data-source-" + k: v for k, v in node.attrib.items() if k != "id"}


def source_rows(table):
    return [n for n in table.iter() if tag(n) == "row"]


def reader_rows(table):
    return [row for group in table if group.tag in ("thead", "tbody") for row in group]


def own_math(node):
    result = []
    for child in node:
        if tag(child) == "math":
            result.append(child)
        elif tag(child) not in ("media", "table", "list", "para"):
            result.extend(own_math(child))
    return result


def own_prose(node):
    result = node.text or ""
    for child in node:
        if tag(child) not in ("math", "link", "media", "table", "list"):
            result += own_prose(child)
        result += child.tail or ""
    return result


def source_specs(source):
    result = {}
    def visit(node, owner=None, index=0):
        name = tag(node)
        if name == "media":
            result[node.get("id") + "/alt"] = node
            return
        if name == "table":
            sid = node.get("id")
            result[sid + "/summary"] = node
            for ri, row in enumerate(source_rows(node), 1):
                result[f"{sid}/row/{ri}/entry/1"] = row[0]
            return
        if name in ("title", "para", "item", "term", "meaning"):
            if name == "title" and owner is source:
                key = "m49301/title"
            elif name == "title" and tag(owner) == "metadata":
                key = "m49301/metadata/title"
            elif name == "term":
                key = owner.get("id") + "/term"
            elif name == "item":
                key = f'{owner.get("id")}/item/{index + 1}'
            else:
                key = node.get("id") or owner.get("id") + "/" + name
            result[key] = node
            for position, child in enumerate(node):
                if tag(child) == "list":
                    visit(child, node, position)
            return
        for position, child in enumerate(node):
            visit(child, node, position)
    visit(source)
    return result


def target_block(document, key, original):
    if tag(original) in ("table", "media"):
        return by_id(document, original.get("id"))
    return marked(document, "data-source-key", key)


def validate_boundary(source, manifest, check=require):
    witnesses = manifest["source_byte_witnesses"]
    canonical, pinned, comparison = [ROOT / witnesses[k] for k in
        ("canonical_checkout_path", "pinned_lf_witness_path", "comparison_path")]
    check("canonical_raw_SHA", hashlib.sha256(canonical.read_bytes()).hexdigest() == witnesses["canonical_checkout_sha256"]
          == "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612")
    check("pinned_LF_SHA", sha256(pinned) == manifest["full_module_sha256"]
          == "81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3")
    check("only4801CR_removed", canonical.read_bytes().count(b"\r") == 4801
          and canonical.read_bytes().replace(b"\r\n", b"\n") == pinned.read_bytes())
    check("Indonesian_raw_SHA", hashlib.sha256(comparison.read_bytes()).hexdigest() == witnesses["comparison_sha256"]
          == "67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a")
    full, indo = ET.parse(pinned).getroot(), ET.parse(comparison).getroot()
    check("pinned_module_manifest_identity", manifest["commit"] == "789b54099106b071d1d32bfcee454fed72eb4768"
          and manifest["module"] == "m49301" and manifest["path"] == "modules/m49301/index.cnxml"
          and manifest["upstream_url"] == "https://github.com/openstax/osbooks-college-algebra-bundle")
    check("root_order_and_original_attributes", [tag(n) for n in source] == ["title", "metadata", "content", "glossary"]
          == [tag(n) for n in full] and full.attrib == manifest["module_metadata"]["root_attributes"] == {}
          and source.attrib == {"id": "m49301-unit-009-excerpt"} and source.tag == full.tag)
    for i in (0, 1, 3):
        check("full_root_component:" + str(i), signature(source[i]) == signature(full[i]) and source[i].tail == full[i].tail)
    check("last_complete_content_child10", len(full[2]) == 10 and len(source[2]) == 1
          and source[2][0].get("id") == full[2][-1].get("id") == SECTION
          and signature(source[2][0]) == signature(full[2][-1]) and source[2][0].tail == full[2][-1].tail)
    check("content_wrapper_prose_and_tail", source[2].attrib == full[2].attrib and source[2].text == full[2].text
          and source[2].tail == full[2].tail)
    check("manifest_boundary", manifest["selection_ids"] == [SECTION] and manifest["next_source_id"] is None
          and manifest["selection_boundary"]["selected_content_child"] ==
          {"index": 10, "tag": "section", "id": SECTION, "coverage": "complete subtree"}
          and manifest["selection_boundary"]["root_order"] == [tag(n) for n in source])
    check("excerpt_digest", sha256(BASE / "source-excerpts/unit-009.cnxml") == manifest["excerpt_sha256"])
    imath = list(by_id(indo, SECTION).iter("{" + MATH + "}math"))
    check("all164_Indonesian_math_witnesses", len(imath) == 164 and [signature(n) for n in imath]
          == [signature(n) for n in source.iter("{" + MATH + "}math")])
    metadata = manifest["module_metadata"]
    check("source_module_metadata_values", metadata["content_id"] == text(source[1][0]) == "m49301"
          and metadata["title"] == text(source[0]) == text(source[1][1]) == metadata["metadata_title"]
          and metadata["uuid"] == text(source[1][-1]) == "11f4eacc-c348-4836-8c5b-747577d249ca"
          and metadata["source_order"] == [tag(n) for n in source[1]])
    check("source_objective_metadata", metadata["abstract_ids"] == [n.get("id") for n in source[1][2]]
          and metadata["objectives"] == len(by_id(source,"list-00001")) == 5)
    count=lambda kind:sum(tag(n)==kind for n in source.iter())
    statistics={"translation_blocks":len(source_specs(source)),"identified_nodes":sum(bool(n.get("id")) for n in source.iter())-1,
        "exercises":count("exercise"),"problems":count("problem"),"supplied_solutions":count("solution"),
        "exercises_without_supplied_solution":sum(len(n)==1 for n in source.iter() if tag(n)=="exercise"),"mathml_trees":count("math"),
        "child_placeholders":sum(tag(c)=="list" for n in source.iter() if tag(n)=="para" for c in n),"links":count("link"),
        "tables":count("table"),"table_rows":count("row"),"table_entries":count("entry"),"images":count("media"),
        "figure_wrappers":count("figure"),"footnotes":count("footnote"),"newlines":count("newline"),
        "circled_part_tokens":sum(tag(n)=="span" and n.get("class")=="token" for n in source.iter()),"superscript_units":count("sup"),
        "glossary_definitions":len(source[3]),"glossary_wording_blocks":sum(tag(n) in ("term","meaning") for n in source[3].iter()),"module_objectives":5}
    check("entire_source_statistics_derived",manifest["source_statistics"]==statistics)
    check("actual_last_source_ID",manifest["selection_boundary"]["last_source_id"]==[n.get("id") for n in source.iter() if n.get("id")][-1])
    modules = [n.get("document") for n in ET.parse(ROOT / manifest["next_collection_module"]["collection_path"]).iter()
               if tag(n) == "module"]
    check("actual_collection_successor", modules[modules.index("m49301") + 1] == manifest["next_collection_module"]["module"] == "m49304")
    return {"selected": SECTION, "root_components": [tag(n) for n in source], "next_collection_module": "m49304",
            "module_completion_claimed": False, "previous_required_modules": ["m50919", "m49299"]}


def validate_structure(document, source, manifest, check=require):
    source_ids = [n.get("id") for n in source.iter() if n is not source and n.get("id")]
    identifiers = [n.get("id") for n in document.iter() if n.get("id")]
    check("437_source_IDs", len(source_ids) == len(set(source_ids)) == 437)
    check("all_reader_IDs_unique", len(identifiers) == len(set(identifiers)))
    check("source_ID_order", [sid for sid in identifiers if sid in source_ids] == source_ids)
    check("no_excerpt_ID_in_reader", source.get("id") not in identifiers)
    op, rp = parents(source), parents(document)
    def lineage(node, mapping):
        result = []
        while node in mapping:
            node = mapping[node]
            if node.get("id") in source_ids:
                result.append(node.get("id"))
        return result
    for original in (n for n in source.iter() if n is not source and n.get("id")):
        check("source_ancestry:" + original.get("id"), lineage(original, op) == lineage(by_id(document, original.get("id")), rp))
    main = document.find("body/main")
    check("complete_main_topology", [(n.tag, n.get("id"), n.get("class")) for n in main] == [
        ("aside", "exercises-source-context", "original"), ("p", None, "source-label"),
        ("h2", None, "source-module-title"), ("div", None, "source-metadata"), ("div", None, "source-content"),
        ("section", None, "source-glossary"), ("section", "exercises-bridge", "original"), ("section", "terminology", None)])
    check("main_text_tails", main.attrib == {} and pure(main))
    label = ET.fromstring('<p class="source-label">ماخذ دا ترجمہ: <bdi dir="ltr" lang="en">OpenStax Precalculus 2e, §1.1</bdi> دے مقصد، حصے دیاں مشقاں تے اصطلاحاں۔</p>')
    check("source_label_exact", signature(main[1]) == signature(label))
    glossary = main[5]
    check("glossary_wrapper_exact", glossary.attrib == {"class": "source-glossary", "aria-labelledby": "source-glossary-title"}
          and [n.tag for n in glossary] == ["h2", "dl"] and pure(glossary)
          and signature(glossary[0]) == signature(ET.fromstring('<h2 id="source-glossary-title">ماخذ دیاں اصطلاحاں</h2>'))
          and glossary[1].attrib == {} and pure(glossary[1]))
    check("glossary11_definitions", len(source[3]) == len(glossary[1]) == 11
          and [(n.tag, n.get("id")) for n in glossary[1]] == [("div", n.get("id")) for n in source[3]])
    exercise_nodes = [n for n in source.iter() if tag(n) == "exercise"]
    structural = {"metadata", "abstract", "content", "section", "exercise", "problem", "solution", "list", "definition"}
    specs = source_specs(source)
    key_by_node = {n: k for k, n in specs.items()}
    def output(node):
        name = tag(node)
        if name == "list":
            return "ol" if node.get("list-type") == "enumerated" else "ul"
        if name == "title":
            return "h2" if op[node] is source or op[node].get("id") == SECTION else "h3"
        if name == "para":
            return "div" if any(tag(c) == "list" for c in node) else "p"
        return {"metadata": "div", "abstract": "div", "content": "div", "content-id": "p", "uuid": "p",
                "section": "section", "exercise": "article", "problem": "div", "solution": "section",
                "item": "li", "table": "div", "media": "div", "definition": "div", "term": "dt", "meaning": "dd"}[name]
    pairings = []
    for original in (n for n in source.iter() if tag(n) in structural):
        name, sid = tag(original), original.get("id")
        target = by_id(document, sid) if sid else marked(document, "data-source-tag", name)
        attrs = {"id": sid} if sid else {}
        if name in ("metadata", "abstract", "content"):
            attrs.update({"class": "source-" + name, "data-source-tag": name})
        elif name == "definition":
            attrs["data-source-tag"] = name
        elif name == "section":
            attrs.update({"class": "translated", **retained_attrs(original)})
        elif name in ("exercise", "problem", "solution"):
            attrs.update({"class": "source-" + name, **retained_attrs(original)})
        elif name == "list":
            attrs.update(retained_attrs(original))
            if any(c.get("class") == "token" for item in original for c in item):
                attrs.update({"class": "source-parts", "role": "list"})
        label_key = sid or name
        check("container_tag_attributes:" + label_key, target.tag == output(original) and target.attrib == attrs)
        expected = []
        if name in ("exercise", "solution"):
            expected.append(("h4" if name == "exercise" else "h5", None, None, None, None))
            heading = (f'<h4>مشق <bdi dir="ltr">{exercise_nodes.index(original)+1}</bdi></h4>' if name == "exercise"
                       else '<h5>ماخذ دا حل</h5>')
            check("local_heading_exact:" + label_key, signature(target[0]) == signature(ET.fromstring(heading)))
        for child in original:
            kind = tag(child)
            expected.append((output(child), None if kind in ("table", "media") else child.get("id"),
                             child.get("id") if kind in ("table", "media") else None,
                             key_by_node.get(child) if kind not in ("table", "media") else None,
                             kind if kind in ("content-id", "uuid") else None))
        actual = [(n.tag, n.get("id"), n.get("data-source-child"), n.get("data-source-key"), n.get("data-source-field")) for n in target]
        check("complete_structural_children:" + label_key, actual == expected)
        check("structural_text_tails:" + label_key, pure(target))
        check("source_structural_prose_not_omitted:" + label_key, not (original.text or "").strip()
              and all(not (n.tail or "").strip() for n in original))
        if name == "exercise":
            kinds = [tag(n) for n in original]
            check("only_actual_problem_and_optional_solution:" + sid, kinds in (["problem"], ["problem", "solution"]))
            pairings.append({"exercise": sid, "problem": original[0].get("id"),
                             "solution": original[1].get("id") if len(original) == 2 else None})
    check("92_exercises46_supplied46_absent", len(pairings) == 92 and sum(p["solution"] is not None for p in pairings) == 46
          and [p["exercise"] for p in pairings] == manifest["exercise_ids"])
    check("no_fabricated_solution_containers", len([n for n in document.iter() if n.get("class") == "source-solution"]) == 46)
    check("all5_objectives", len(by_id(source, "list-00001")) == len(by_id(document, "list-00001")) == 5)
    check("no_source_figures_or_footnotes", not any(tag(n) in ("figure", "footnote") for n in source.iter())
          and not any(n.tag == "figure" or n.get("class") == "source-endnotes" for n in document.iter()))
    for child in source[1]:
        if tag(child) in ("content-id", "uuid"):
            field = tag(child)
            expected = ET.fromstring(f'<p class="metadata-value" dir="ltr" data-source-field="{field}"><bdi dir="ltr" lang="en">{html.escape(child.text)}</bdi></p>')
            check("raw_metadata_field:" + field, signature(marked(document, "data-source-field", field)) == signature(expected))
    return {"source_ids": source_ids, "exercise_pairings": pairings, "module_objectives": 5, "glossary_definitions": 11}


def validate_blocks(document, source, translation, manifest, check=require):
    specs, blocks, op = source_specs(source), translation["source_blocks"], parents(source)
    check("244_source_keys_in_order", len(specs) == len(blocks) == 244 and list(specs) == list(blocks) == manifest["source_block_keys"])
    check("exact_key_markers_no_extras", [n.get("data-source-key") for n in document.iter() if n.get("data-source-key")]
          == [key for key, n in specs.items() if tag(n) not in ("table", "media")])
    totals = {"math": 0, "link": 0, "child": 0, "newlines": 0, "parts": 0, "strong": 0, "underline": 0, "sup": 0}
    numerals = {}
    for key, original in specs.items():
        name, value = tag(original), blocks[key]
        target = target_block(document, key, original)
        if name in ("table", "media"):
            attr = "summary" if name == "table" else "alt"
            check("faithful_attribute:" + key, target.get("data-source-" + attr) == value and "{{" not in value)
            source_prose, translated_prose = original.get(attr), value
        else:
            if name != "entry":
                owner = op[original]
                kind = ("h2" if owner is source or owner.get("id") == SECTION else "h3") if name == "title" else {
                    "para": "p", "item": "li", "term": "dt", "meaning": "dd"}[name]
                attrs = {"id": original.get("id")} if original.get("id") else {}
                attrs["data-source-key"] = key
                if owner is source:
                    attrs["class"] = "source-module-title"
                if name == "para" and any(tag(n) == "list" for n in original):
                    kind = "div"
                    attrs.update({"class": "source-para", "data-source-tag": "para"})
                check("block_tag_attributes:" + key, target.tag == kind and target.attrib == attrs)
            groups = {"math": own_math(original), "link": [n for n in original if tag(n) == "link"],
                      "child": [n for n in original if tag(n) == "list"]}
            for kind, nodes in groups.items():
                check("ordered_" + kind + "_slots:" + key, re.findall(r"\{\{" + kind + r":(\d+)\}\}", value) == [str(i) for i in range(len(nodes))])
                totals[kind] += len(nodes)
            expected = ET.fromstring("<fragment>" + re.sub(r"\{\{(math|link|child):(\d+)\}\}", r'<slot kind="\1" index="\2" />', value) + "</fragment>")
            actual, counts = copy.deepcopy(target), {"math": 0, "link": 0, "child": 0}
            children = [n.get("id") for n in groups["child"]]
            def slots(node):
                for index, child in enumerate(list(node)):
                    kind = ("math" if child.get("class") == "math-isolate" else "link" if child.get("data-source-link")
                            else "child" if child.get("id") in children else None)
                    if kind:
                        if kind == "child":
                            check("actual_child_slot_order:" + key, child.get("id") == children[counts[kind]])
                        replacement = ET.Element("slot", {"kind": kind, "index": str(counts[kind])})
                        counts[kind] += 1
                        replacement.tail = child.tail
                        node.remove(child)
                        node.insert(index, replacement)
                    else:
                        slots(child)
            slots(actual)
            check("exact_block_fragment:" + key, content_signature(actual) == content_signature(expected))
            check("actual_slot_counts:" + key, counts == {k: len(v) for k, v in groups.items()})
            styles = ["u" if n.get("effect") == "underline" else "em" if n.get("effect") == "italics" else "strong"
                      for n in original if tag(n) == "emphasis"]
            check("source_emphasis_style:" + key, [n.tag for n in target if n.tag in ("u", "em", "strong")] == styles)
            totals["strong"] += styles.count("strong")
            totals["underline"] += styles.count("u")
            newline_count = sum(tag(n) == "newline" for n in original)
            check("source_newlines:" + key, len(target.findall("br")) == newline_count)
            totals["newlines"] += newline_count
            tokens = [n.text for n in original if tag(n) == "span" and n.get("class") == "token"]
            labels = [n for n in target if n.get("class") == "part-label"]
            check("source_part_tokens:" + key, len(tokens) == len(labels) and all(n.tag == "span" and n.attrib == {"class": "part-label", "dir": "ltr"}
                  and len(n) == 0 and n.text == "(" + chr(ord("a") + "ⓐⓑⓒⓓ".index(token)) + ")" for n, token in zip(labels, tokens)))
            totals["parts"] += len(tokens)
            supers = [n for n in original if tag(n) == "sup"]
            check("source_superscript_units:" + key, [text(n) for n in target.iter("sup")] == [text(n) for n in supers])
            totals["sup"] += len(supers)
            clean = ET.fromstring("<fragment>" + re.sub(r"\{\{(?:math|link|child):\d+\}\}", "", value) + "</fragment>")
            allowed_inline={"br":[{}],"strong":[{}],"u":[{}],"sup":[{}],
                            "span":[{"class":"part-label","dir":"ltr"}],
                            "bdi":[{"dir":"ltr"},{"dir":"ltr","lang":"en"}]}
            check("source_inline_markup_allowlist:"+key,all(n.tag in allowed_inline and n.attrib in allowed_inline[n.tag]
                  for n in clean.iter() if n is not clean))
            source_prose, translated_prose = own_prose(original), text(clean)
        digits = re.findall(r"\d+(?:\.\d+)?", source_prose)
        check("source_plain_numbers:" + key, re.findall(r"\d+(?:\.\d+)?", translated_prose) == digits)
        if digits:
            numerals[key] = digits
    check("all_source_inline_counts", totals == {"math": 164, "link": 1, "child": 3, "newlines": 11, "parts": 38,
          "strong": 6, "underline": 1, "sup": 2})
    check("final_underlined_not", text(by_id(document, "fs-id1165137844421").find("u")) == "نہیں")
    return {"keys": list(specs), "inline_counts": totals, "plain_numbers": numerals}


def math_contexts(document, source, rendered=False):
    owners = {(target_block(document, key, n) if rendered else n): key for key, n in source_specs(source).items()
              if tag(n) not in ("table", "media")}
    root = document if rendered else source
    p, result, counts = parents(root), [], {}
    for node in root.iter("{" + MATH + "}math"):
        while node in p:
            node = p[node]
            if node in owners:
                key = owners[node]
                result.append((key, counts.get(key, 0)))
                counts[key] = counts.get(key, 0) + 1
                break
        else:
            raise AssertionError("math_actual_source_owner")
    return result


def allowed_edits(original, context):
    leaves = [(path, node) for path, node in paths(original) if not len(node)]
    allowed = {}
    remainder = list(leaves)
    while remainder and tag(remainder[-1][1]) == "mo" and remainder[-1][1].text in (".", ","):
        path, leaf = remainder.pop()
        allowed[path] = (leaf.text, "")
    if context in NUMERIC_EDGES:
        path, leaf = remainder[-1]
        before = NUMERIC_EDGES[context]
        require("independent_exact_MN_source_position", tag(leaf) == "mn" and leaf.text == before
                and re.fullmatch(r"−?\d+\.", before) is not None)
        after = before[:-1]
        require("unchanged_numeric_semantics", float(before.replace("−", "-")) == float(after.replace("−", "-")))
        allowed[path] = (before, after)
    return allowed


def restore_math(original, actual, context, check=require):
    label, raw = str(context), actual.get(LEDGER)
    check("math_root_LTR:" + label, actual.get("dir") == "ltr")
    try:
        entries = [] if raw is None else json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise AssertionError("ledger_JSON") from error
    check("ledger_list_nonempty_if_present:" + label, isinstance(entries, list) and (raw is None or bool(entries)))
    allowed, restored, seen = allowed_edits(original, context), copy.deepcopy(actual), set()
    for entry in entries:
        check("ledger_schema:" + label, isinstance(entry, dict) and set(entry) == {"path", "old", "new"}
              and isinstance(entry["path"], list) and all(type(i) is int and i >= 0 for i in entry["path"])
              and isinstance(entry["old"], str) and isinstance(entry["new"], str))
        path = tuple(entry["path"])
        check("ledger_unique_path:" + label, path not in seen)
        seen.add(path)
        check("source_position_whitelist:" + label, path in allowed)
        before, after = allowed[path]
        left, right = at_path(original, path), at_path(restored, path)
        check("ledger_old_matches_source:" + label, entry["old"] == before == left.text)
        check("ledger_new_matches_policy:" + label, entry["new"] == after)
        check("ledger_new_matches_display:" + label, (right.text or "") == after)
        check("ledger_leaf_topology:" + label, left.tag == right.tag and len(left) == len(right) == 0)
        right.text = before
    check("complete_required_ledger:" + label, seen == set(allowed))
    restored.attrib.pop("dir")
    restored.attrib.pop(LEDGER, None)
    check("exact_math_reconstruction:" + label, signature(restored) == signature(original))
    return entries


def validate_math(document, source, check=require):
    originals = list(source.iter("{" + MATH + "}math"))
    actual = [n for n in document.iter() if tag(n) == "math"]
    check("164_exact_namespace_trees", len(originals) == len(actual) == 164 and all(n.tag == "{" + MATH + "}math" for n in actual))
    contexts = math_contexts(document, source)
    check("164_exact_math_owners_slots", contexts == math_contexts(document, source, True))
    p, edits = parents(document), []
    for i, (left, right, context) in enumerate(zip(originals, actual, contexts)):
        wrapper = p[right]
        attrs = {"class": "math-isolate", "dir": "ltr", "data-source-owner": context[0], "data-source-slot": str(context[1])}
        if any(tag(n) == "mtable" for n in left.iter()) or len(list(left.iter())) > 70:
            attrs.update({"tabindex": "0", "role": "region", "aria-label": "ریاضی دا فارمولا؛ لوڑ پئے تے پاسے سرکاؤ"})
        check("math_wrapper_attributes:" + str(i), wrapper.tag == "span" and wrapper.attrib == attrs)
        check("math_wrapper_pure:" + str(i), len(wrapper) == 1 and wrapper[0] is right and pure(wrapper))
        edits.extend({"tree": i, "owner": context[0], "slot": context[1], **row} for row in restore_math(left, right, context, check))
    check("ledgers_only_source_math", all(n in actual for n in document.iter() if LEDGER in n.attrib))
    check("exact40edits14MN26MO", len(edits) == 40 and sum((r["owner"], r["slot"]) in NUMERIC_EDGES for r in edits) == 14
          and set(NUMERIC_EDGES).issubset(contexts))
    return {"trees": 164, "contexts": contexts, "edits": edits, "numeric_owner_whitelist": [
        {"owner": k[0], "slot": k[1], "old": v, "new": v[:-1]} for k, v in NUMERIC_EDGES.items()]}


def validate_tables(document, source, translation, check=require):
    originals = [n for n in source.iter() if tag(n) == "table"]
    check("four_actual_table_IDs", [n.get("id") for n in originals] == TABLES
          and len([n for n in document.iter("table") if n.get("class") == "source-table"]) == 4)
    check("four_summary_overrides", set(translation["table_summary_overrides"]) == set(TABLES))
    rp, report = parents(document), []
    for original in originals:
        sid = original.get("id")
        target = by_id(document, sid)
        group = next(n for n in original if tag(n) == "tgroup")
        cols = [n for n in group if tag(n) == "colspec"]
        labels = [n for n in original if tag(n) == "label"]
        attrs = {"id": sid, "class": "source-table", "dir": "ltr", "data-source-summary": translation["source_blocks"][sid + "/summary"],
                 "aria-label": translation["table_summary_overrides"][sid], "aria-describedby": "exercises-table-summary",
                 "data-description-origin": "original-correction", **{"data-source-" + k: v for k, v in original.attrib.items() if k not in ("id", "summary")},
                 **{"data-source-tgroup-" + k: v for k, v in group.attrib.items()}}
        if labels:
            check("source_empty_table_label:" + sid, len(labels) == 1 and len(labels[0]) == 0 and not text(labels[0]))
            attrs["data-source-empty-label"] = "true"
        check("table_exact_attributes:" + sid, target.tag == "table" and target.attrib == attrs
              and original.get("summary") == target.get("data-source-summary") == ".." and target.get("aria-label") != "..")
        groups = [n for n in group if tag(n) in ("thead", "tbody")]
        check("table_exact_child_groups:" + sid, [n.tag for n in target] == (["colgroup"] if cols else []) + [tag(n) for n in groups] and pure(target))
        if cols:
            cg = target[0]
            check("colgroup_structure:" + sid, cg.attrib == {} and pure(cg) and len(cg) == len(cols) == int(group.get("cols")))
            for i, (left, right) in enumerate(zip(cols, cg)):
                check(f"source_colspec:{sid}:{i}", right.tag == "col" and len(right) == 0 and right.text in (None, "")
                      and right.attrib == retained_attrs(left))
        for left, right in zip(groups, list(target)[1 if cols else 0:]):
            check("table_group_structure:" + sid, right.tag == tag(left) and right.attrib == retained_attrs(left)
                  and len(right) == len(left) and pure(right))
        left_rows, right_rows = source_rows(original), reader_rows(target)
        check("table_row_count:" + sid, len(left_rows) == len(right_rows) == 2)
        matrix = []
        for ri, (left, right) in enumerate(zip(left_rows, right_rows), 1):
            check(f"table_row_shape:{sid}:{ri}", right.tag == "tr" and right.attrib == retained_attrs(left) and pure(right)
                  and len(left) == len(right) == int(group.get("cols")))
            row_values = []
            for ci, (entry, cell) in enumerate(zip(left, right), 1):
                key = f"{sid}/row/{ri}/entry/{ci}"
                cell_attrs = {"dir": "ltr", **retained_attrs(entry)}
                if entry.get("align") == "center":
                    cell_attrs["style"] = "text-align:center"
                if ci == 1:
                    cell_attrs.update({"scope": "row", "data-source-key": key})
                check("table_cell_semantics:" + key, cell.tag == ("th" if ci == 1 else "td") and cell.attrib == cell_attrs)
                if ci > 1:
                    check("table_data_exact:" + key, len(entry) == len(cell) == 0 and cell.text == text(entry))
                row_values.append(text(cell))
            matrix.append(row_values)
        wrapper = rp[target]
        check("table_scroll_wrapper:" + sid, wrapper.tag == "div" and wrapper.attrib == {
            "class": "table-scroll source-table-scroll", "dir": "ltr", "tabindex": "0", "role": "region", "aria-label": "جدول؛ لوڑ پئے تے پاسے سرکاؤ"}
            and len(wrapper) == 1 and wrapper[0] is target and pure(wrapper))
        container = rp[wrapper]
        check("table_container_pure:" + sid, container.tag == "div" and container.attrib == {"class": "source-table-container", "data-source-child": sid}
              and len(container) == 2 and container[0] is wrapper and pure(container))
        advisory = ET.fromstring('<p class="scroll-hint source-summary-advisory">ماخذ دے خالی خلاصے بارے <a href="#exercises-table-summary">ساڈی اصل وضاحت ویکھو</a>۔</p>')
        check("table_advisory_exact:" + sid, signature(container[1]) == signature(advisory))
        report.append({"id": sid, "rows": len(left_rows), "columns": int(group.get("cols")), "cells": matrix,
                       "source_colspec_count": len(cols), "source_empty_label": bool(labels)})
    check("four_exact_shapes_and_colspecs", [(r["rows"], r["columns"], r["source_colspec_count"], r["source_empty_label"]) for r in report]
          == [(2, 4, 4, True)] * 3 + [(2, 11, 0, False)])
    return report


def validate_images(document, source, translation, manifest, notices, check=require):
    originals = [n for n in source.iter() if tag(n) == "media"]
    check("26_images_and_notices", len(originals) == len(manifest["images"]) == len(notices) == len(list(document.iter("img"))) == 26)
    with (ROOT / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv").open(encoding="utf-8-sig", newline="") as stream:
        rights = list(csv.DictReader(stream))
    op, rp, report, note_map = parents(source), parents(document), [], {}
    corrections = {"fs-id1165135541720", "fs-id1165134380356", "fs-id1165134031257", "fs-id1165135457089", "fs-id1165135259631", "fs-id1165135407024"}
    for i, (original, spec, notice) in enumerate(zip(originals, manifest["images"], notices)):
        sid, actual = original.get("id"), by_id(document, original.get("id"))
        check("actual_direct_media_no_figure_ID:" + sid, spec["media_id"] == sid and "figure_id" not in spec and "local_label" not in spec
              and tag(op[original]) == ("problem" if i < 20 else "solution") and len(original) == 1 and tag(original[0]) == "image")
        check("source_image_path_MIME:" + sid, original[0].get("src") == "../../" + spec["source_path"] and original[0].get("mime-type") == "image/jpg")
        filename = re.fullmatch(r"media/CNX_Precalc_Figure_01_01_(\d{3})-[a-z0-9]+\.jpg", spec["source_path"])
        check("safe_declared_asset_path:" + sid, filename is not None and spec["path"] == "assets/Exercise_01_01_" + filename[1] + ".jpg")
        asset = BASE / spec["path"]
        canonical = ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle" / spec["source_path"]
        indo = ROOT / "downloads/extracted/A30/repo/source" / spec["source_path"]
        check("unchanged_three_image_witnesses:" + sid, asset.read_bytes() == canonical.read_bytes() == indo.read_bytes()
              and sha256(asset) == spec["sha256"] == notice["sha256"])
        dimensions = jpeg_dimensions(asset.read_bytes())
        check("source_JPEG_dimensions:" + sid, list(dimensions) == [spec["width"], spec["height"]])
        matches = [row for row in rights if row["asset_path"] == spec["source_path"]]
        check("exact_existing_whole_notice:" + sid, len(matches) == 1 and notice == matches[0]
              and notice["rights_component_id"] == spec["rights_component_id"] and int(notice["bytes"]) == asset.stat().st_size)
        check("admitted_default_credit_binding:" + sid, notice["admission"] == "admitted" and notice["license_id"] == "CC-BY-NC-SA-4.0"
              and notice["classification"] == "WORK_DEFAULT_UNCREDITED_ART" and "m49301" in notice["source_modules"].split(";")
              and notice["attribution"] == "Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0.")
        check("original_alt_witness:" + sid, spec["source_alt"] == original.get("alt"))
        note = "exercises-alt-corrections" if sid in corrections else "exercises-alt-206" if sid == "fs-id1165137439470" else "exercises-alt-general"
        note_map[sid] = note
        attrs = {"id": sid, "src": "../" + spec["path"], "alt": translation["image_alt_overrides"][sid],
                 "data-source-alt": translation["source_blocks"][sid + "/alt"], "aria-describedby": note,
                 "data-description-origin": "original-accessibility-addition", "width": str(dimensions[0]), "height": str(dimensions[1]),
                 "style": f"--source-width:{dimensions[0]}px", **{"data-source-" + k: v for k, v in original.attrib.items() if k not in ("id", "alt")}}
        check("image_exact_attributes:" + sid, actual.tag == "img" and actual.attrib == attrs and len(actual) == 0 and actual.text in (None, ""))
        wrapper = rp[actual]
        check("image_focus_wrapper:" + sid, wrapper.tag == "div" and wrapper.attrib == {"class": "figure-scroll", "dir": "ltr", "tabindex": "0",
              "role": "region", "aria-label": "اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ"} and len(wrapper) == 1 and wrapper[0] is actual and pure(wrapper))
        container = rp[wrapper]
        check("media_container_pure:" + sid, container.tag == "div" and container.attrib == {"class": "source-media", "data-source-child": sid}
              and len(container) == 3 and container[0] is wrapper and pure(container))
        hint = ET.fromstring(f'<p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="../{spec["path"]}">اصل شکل وکھری کھولو</a>۔</p>')
        advisory = ET.fromstring(f'<p class="scroll-hint source-alt-advisory">متبادل متن بارے <a href="#{note}">ساڈی وکھری اصل وضاحت ویکھو</a>۔</p>')
        check("image_advisory_exact:" + sid, signature(container[1]) == signature(hint) and signature(container[2]) == signature(advisory))
        check("image_note_separate_original:" + sid, by_id(document, note) in list(by_id(document, "exercises-bridge").iter()))
        report.append({"media_id": sid, "exercise_part": tag(op[original]), "asset": spec["path"], "sha256": spec["sha256"],
                       "dimensions": dimensions, "notice": notice["rights_component_id"], "original_note": note})
    check("all26_alt_mappings", translation["image_alt_note_ids"] == note_map and set(translation["image_alt_overrides"]) == set(note_map))
    return report


def validate_links(document, source, manifest, check=require):
    source_links = [(key, i, link) for key, original in source_specs(source).items() if tag(original) not in ("table", "media")
                    for i, link in enumerate(n for n in original if tag(n) == "link")]
    check("one_local_source_link", len(source_links) == 1 and source_links[0][0] == "fs-id1165135641701"
          and source_links[0][2].attrib == {"target-id": TABLES[3]})
    expected_ref = {"id": TABLES[3], "kind": "table", "local_label": "1.1.15", "unit": "PNB-009", "href": "#" + TABLES[3]}
    check("one_source_reference_manifest", manifest["references"] == [expected_ref])
    marker = source_links[0][0] + "/link/0"
    actual = [n for n in document.iter() if n.get("data-source-link")]
    expected = ET.fromstring(f'<a href="#{TABLES[3]}" data-source-link="{marker}">جدول <bdi dir="ltr">1.1.15</bdi></a>')
    check("one_exact_source_link", len(actual) == 1 and signature(actual[0]) == signature(expected)
          and parents(document)[actual[0]] is by_id(document, source_links[0][0]))
    local = []
    for node in document.iter():
        for attr in ("href", "src"):
            if not node.get(attr):
                continue
            value = node.get(attr)
            address = urlsplit(value)
            if address.scheme in ("http", "https", "mailto"):
                continue
            check("local_scheme:" + value, not address.scheme and not address.netloc)
            path = (READER.parent / unquote(address.path)).resolve() if address.path else READER.resolve()
            check("local_path:" + value, path.is_relative_to(BASE.resolve()) and path.is_file())
            if address.fragment:
                target = document if path == READER.resolve() else parse_reader(path.read_text(encoding="utf-8"))
                check("local_fragment:" + value, len([n for n in target.iter() if n.get("id") == unquote(address.fragment)]) == 1)
            local.append(value)
    return {"source_link": expected_ref, "local_destinations": local}


def validate_bridge(document, source, translation, check=require):
    rp, report = parents(document), []
    for key in ("bridge_before_html", "bridge_after_html"):
        expected = ET.fromstring(translation[key])
        actual = by_id(document, expected.get("id"))
        check("original_fragment_exact:" + key, signature(actual) == signature(expected))
        check("original_separate_from_source:" + key, rp[actual] is document.find("body/main") and actual.get("class") == "original")
        check("no_original_MathML_or_source_marker:" + key, not any(tag(n) == "math" or n.get("data-source-key") for n in actual.iter()))
        report.append(expected.get("id"))
    check("source_conditions_really_present", any("h≠0" in compact(text(n)) for n in by_id(source, "fs-id1165135195668").iter() if tag(n) == "math")
          and any("x≠a" in compact(text(n)) for n in by_id(source, "fs-id1165135579707").iter() if tag(n) == "math"))
    check("bridge_h_and_x_conditions_labeled", "h ≠ 0" in text(by_id(document, "exercises-domains")) and "x ≠ a" in text(by_id(document, "exercises-domains")))
    check("rounded_source_equalities_preserved", all("=" in text(n) and "≈" not in text(n)
          for n in by_id(document, "fs-id1165137755505").iter("{" + MATH + "}math")))
    check("original_rounding_note_exact_values", [text(n) for n in by_id(document, "exercises-rounded-equality").iter("bdi")]
          == ["4.414", "4.732", "5.236", "3+√2 ≈ 4.414", "3+√3 ≈ 4.732", "3+√5 ≈ 5.236"])
    keytable = by_id(document, "exercises-term-key")
    check("nine_bilingual_bridge_rows", len(keytable.findall("tbody/tr")) == 9 and all(
        len(row) == 3 and row[1].get("lang") == "ur-Arab-PK" and row[2].attrib == {"lang": "en", "dir": "ltr"}
        for row in keytable.findall("tbody/tr")))
    return report


def validate_unicode(document, check=require):
    check("reader_unicode_gate", FORBIDDEN.search(ET.tostring(document, encoding="unicode")) is None)


def validate_directions(document, source, check=require):
    rp = parents(document)
    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = rp.get(node)
        return None
    check("reader_language_and_direction", document.attrib == {"lang": "pnb-Arab-PK", "dir": "rtl"})
    for key, original in source_specs(source).items():
        if tag(original) not in ("table", "media", "entry"):
            check("source_prose_RTL:" + key, direction(target_block(document, key, original)) == "rtl")
    for i, node in enumerate(document.iter()):
        if node.tag in ("style", "title") or tag(node) in ("mi", "mo", "mn", "mtext"):
            continue
        if re.search(r"[A-Za-z0-9]", node.text or ""):
            check("visible_Latin_digits_LTR:" + str(i), direction(node) == "ltr")
        if re.search(r"[A-Za-z0-9]", node.tail or ""):
            check("visible_tail_LTR:" + str(i), direction(rp[node]) == "ltr")


def formula(node):
    """Small independent loss-aware serialization used only for arithmetic QA."""
    name = tag(node)
    if name in ("mi", "mn", "mo", "mtext"):
        return compact(node.text or "").replace("−", "-")
    if name in ("math", "mrow", "mtd"):
        return "".join(formula(n) for n in node)
    if name == "msup":
        return "(" + formula(node[0]) + ")^(" + formula(node[1]) + ")"
    if name == "mfrac":
        return "(" + formula(node[0]) + ")/(" + formula(node[1]) + ")"
    if name == "msqrt":
        return "sqrt(" + "".join(formula(n) for n in node) + ")"
    if name == "mroot":
        return "root(" + formula(node[0]) + "," + formula(node[1]) + ")"
    if name == "mspace":
        return ""
    raise AssertionError("unsupported_arithmetic_MathML:" + name)


def evaluate(expression, env=None):
    """Bounded numeric expression parser; no eval, executable code or CAS imports."""
    env = env or {}
    expression = expression.rstrip(";:.")
    tokens = re.findall(r"sqrt|root|[A-Za-z]|\d+(?:\.\d*)?|\.\d+|[()+*/^,|\-]", expression)
    require("arithmetic_tokens_complete:" + expression, "".join(tokens) == expression)
    position = 0
    def peek():
        return tokens[position] if position < len(tokens) else None
    def take(value=None):
        nonlocal position
        found = peek()
        require("arithmetic_token:" + str(value), found is not None and (value is None or found == value))
        position += 1
        return found
    def atom():
        token = take()
        if token == "(":
            value = summation()
            take(")")
            return value
        if token == "|":
            value = summation()
            take("|")
            return abs(value)
        if re.fullmatch(r"\d+(?:\.\d*)?|\.\d+", token):
            return float(token)
        require("known_arithmetic_symbol:" + token, token in env or token in ("sqrt", "root"))
        if token in ("sqrt", "root") or callable(env.get(token)):
            take("(")
            first = summation()
            if token == "root":
                take(",")
                degree = summation()
                require("real_cube_root_degree", degree == 3)
                value = math.cbrt(first)
            elif token == "sqrt":
                value = math.sqrt(first)
            else:
                value = env[token](first)
            take(")")
            return value
        return env[token]
    def power():
        value = atom()
        if peek() == "^":
            take("^")
            value **= unary()
        return value
    def unary():
        if peek() in ("+", "-"):
            return (-1 if take() == "-" else 1) * unary()
        return power()
    def product():
        value = unary()
        while True:
            token = peek()
            if token in ("*", "/"):
                op = take()
                rhs = unary()
                value = value * rhs if op == "*" else value / rhs
            elif token is not None and (token == "(" or re.fullmatch(r"[A-Za-z]|sqrt|root|\d+(?:\.\d*)?|\.\d+", token)):
                value *= unary()
            else:
                return value
    def summation():
        value = product()
        while peek() in ("+", "-"):
            op = take()
            value += (1 if op == "+" else -1) * product()
        return value
    result = summation()
    require("arithmetic_all_tokens_used:" + expression, position == len(tokens))
    require("arithmetic_real_finite", isinstance(result, (int, float)) and math.isfinite(result))
    return result


def interval(node):
    """Keep thousands separators distinct from the one interval delimiter."""
    raw = formula(node)
    require("closed_interval_brackets", raw.startswith("[") and raw.endswith("]"))
    number = r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    match = re.fullmatch(r"\[(" + number + r"),(" + number + r")\]", raw)
    require("exact_two_interval_endpoints:" + raw, match is not None)
    values = [float(match[i].replace(",", "")) for i in (1, 2)]
    require("interval_order", values[0] <= values[1])
    return values


def validate_arithmetic(document, source, check=require):
    source_ex = [n for n in source.iter() if tag(n) == "exercise"]
    target_ex = [by_id(document, n.get("id")) for n in source_ex]
    def trees(root):
        return list(root.iter("{" + MATH + "}math"))
    def problem(number, rendered=True):
        ex = source_ex[number - 1]
        return by_id(document, ex[0].get("id")) if rendered else ex[0]
    def solution(number, rendered=True):
        ex = source_ex[number - 1]
        require("solution_is_actually_supplied", len(ex) == 2)
        return by_id(document, ex[1].get("id")) if rendered else ex[1]
    def close(left, right):
        return math.isclose(left, right, rel_tol=1e-10, abs_tol=1e-10)
    for expression,env,expected in [("-2^2",{},-4),("(-2)^2",{},4),("2xy",{"x":2,"y":3},12),
                                    ("root(-8,3)",{},-2),("3^(x)",{"x":-2},1/9),("|-3|-|2|",{},1)]:
        check("limited_parser_regression:"+expression,close(evaluate(expression,env),expected))
    for expression,env,error in [("sqrt(-1)",{},ValueError),("1/(x)",{"x":0},ZeroDivisionError),
                                  ("root(-1,2)",{},AssertionError),("unknown(1)",{},AssertionError)]:
        try:
            evaluate(expression,env)
        except error:
            check("limited_parser_rejects:"+expression,True)
        else:
            raise AssertionError("limited_parser_domain_not_rejected:"+expression)
    def equation_values(tree, env):
        parts = formula(tree).rstrip(";:.").split("=")
        require("arithmetic_actual_equality", len(parts) >= 2)
        return [evaluate(part, env) for part in parts]
    classifications = {}
    for number in [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 41, 43, 45, 47, 49, 51, 55, 57, 59, 61, 63, 65]:
        english = text(solution(number, False))
        actual = " ".join(text(n) for n in list(solution(number))[1:])
        expected = {"function": "فنکشن", "not a function": "فنکشن نہیں", "one-to-one function": "اک توں اک فنکشن",
                    "function, but not one-to-one": "فنکشن اے، پر اک توں اک نہیں",
                    "not a function so it is also not a one-to-one function": "فنکشن نہیں، ایس لئی اک توں اک فنکشن وی نہیں"}[english]
        check("supplied_answer_polarity:" + str(number), actual.rstrip("۔") == expected)
        classifications[str(number)] = {"source": english, "rendered": actual}
    # Literal relations: test all actual pairs, not an arbitrary sample subset.
    pair_reports = []
    for number in (6, 7, 60, 61, 62):
        left = formula(trees(problem(number, False))[0])
        right = formula(trees(problem(number))[0])
        check("literal_relation_exact:" + str(number), left.rstrip(".,") == right.rstrip(".,"))
        pairs = re.findall(r"\(([a-d]|-?\d+),([a-d]|-?\d+)\)", right)
        require("source_literal_pairs_parsed", len(pairs) in (3, 4))
        functional = all(len({y for x, y in pairs if x == entry}) == 1 for entry in {x for x, _ in pairs})
        check("literal_relation_function:" + str(number), functional == (number not in (6, 62)))
        pair_reports.append({"exercise": number, "pairs": pairs, "function": functional,
                             "letters_assumed_distinct": number < 8})
    # Bind sampled equations to actual source questions; exact trees are checked above.
    analytic = []
    positive_rules = {8: lambda x:(10-5*x)/2, 9:lambda x:x*x, 11:lambda x:14-3*x*x,
        13:lambda x:-2*x*x+40*x, 14:lambda x:1/x, 15:lambda x:(x+5)/(7*x-3),
        17:lambda x:(3*x+5)/(7*x-1), 19:lambda x:1/(2*x), 20:math.cbrt,
        21:lambda x:x**3, 22:lambda x:math.sqrt(1-x*x), 26:lambda x:math.cbrt(x*x)}
    for number, rule in positive_rules.items():
        expression = formula(trees(problem(number))[0]).rstrip(".,")
        check("relation_equation_source_bound:" + str(number), expression == formula(trees(problem(number, False))[0]).rstrip(".,"))
        xs = [-0.5, 0.5] if number == 22 else [-2, -1, 0.5, 2, 3]
        for x in xs:
            values = [evaluate(part, {"x": x, "y": rule(x)}) for part in expression.split("=")]
            check(f"relation_unique_formula_sample:{number}:{x}", len(values) == 2 and close(*values))
        analytic.append({"exercise": number, "sample_inputs": xs, "limit": "Equation substitution regression; uniqueness reasoning separately reviewed, samples are not proof."})
    for number, x, ys in [(10, 4, [-2, 2]), (12, 1, [-2, 2]), (16, 0, [-1, 1]), (18, 0, [-3, 3]), (25, 2, [-2, 2])]:
        expression = formula(trees(problem(number))[0]).rstrip(".,")
        for y in ys:
            values = [evaluate(part, {"x": x, "y": y}) for part in expression.split("=")]
            check(f"actual_two_output_counterexample:{number}:{y}", len(values) == 2 and close(*values))
        analytic.append({"exercise": number, "counterexample_input": x, "outputs": ys})
    check("plusminus_roles_preserved", formula(trees(problem(23))[0]) == "x=±sqrt(1-y)"
          and formula(trees(problem(24))[0]) == "y=±sqrt(1-x)")
    check("plusminus_direction_counterexample", 1 == math.sqrt(1-0) and -1 == -math.sqrt(1-0))
    evaluations = []
    for number in (27, 29, 31):
        rule = formula(trees(problem(number))[0]).rstrip(".,").split("=", 1)[1]
        check("five_substitution_answer_trees:" + str(number), len(trees(solution(number))) == 5)
        for a, h in [(-1, .25), (0, 1), (.5, .5)]:
            env = {"a": a, "h": h, "f": lambda x, r=rule:evaluate(r, {"x": x})}
            for i, tree in enumerate(trees(solution(number))):
                values = equation_values(tree, env)
                check(f"substitution_numeric_equality:{number}:{a}:{h}:{i}", all(close(values[0], v) for v in values[1:]))
        evaluations.append({"exercise": number, "answers": 5, "rule": rule, "symbolic_sampling": [[-1,.25],[0,1],[.5,.5]]})
    # Difference quotients have explicit source nonzero hypotheses, not invented ones.
    g32 = formula(trees(problem(32))[0]).rstrip(",").split("=", 1)[1]
    q32 = formula(trees(problem(32))[1]).split(",", 1)[0]
    g33 = formula(trees(problem(33))[0]).rstrip(",").split("=", 1)[1]
    eq33 = formula(trees(solution(33))[0]).split(",", 1)[0]
    for x, a, h in [(-2,1,.5),(0,-1,2),(3,.5,-1)]:
        check(f"difference_quotient32:{x}:{h}", close(evaluate(q32, {"x":x,"h":h,"g":lambda v:evaluate(g32,{"x":v})}), -2*x-h))
        vals = [evaluate(part,{"x":x,"a":a,"g":lambda v:evaluate(g33,{"x":v})}) for part in eq33.split("=")]
        check(f"difference_quotient33:{x}:{a}", close(*vals))
    check("source_nonzero_conditions_retained", "h≠0" in compact(text(problem(32))) and "x≠a" in compact(text(problem(33)))
          and "x≠a" in compact(text(solution(33))))
    for number, rule in [(35,lambda x:8-3*x),(37,lambda x:x*x-3*x),(39,lambda t:6-2*t/3)]:
        maths = trees(solution(number))
        for i, tree in enumerate(maths):
            value = formula(tree).rstrip(";.,")
            if value.startswith("f("):
                for t in [-3,0,2]:
                    vals = equation_values(tree,{"f":rule,"t":t})
                    check(f"evaluate_supplied_formula:{number}:{i}:{t}", all(close(vals[0],v) for v in vals[1:]))
            elif re.fullmatch(r"[xt]=-?\d+\.?", value):
                root = float(value.split("=")[1])
                expected_output = {35:-1,37:4,39:2}[number]
                check(f"solve_supplied_root:{number}:{i}", close(rule(root),expected_output))
    # Table tests operate on all displayed pairs and preserve orientation.
    matrices = []
    for sid in TABLES:
        rows = reader_rows(by_id(document,sid))
        values = [[int(text(cell)) for cell in row[1:]] for row in rows]
        source_values = [[int(text(cell)) for cell in row[1:]] for row in source_rows(by_id(source,sid))]
        check("numeric_table_source_values:"+sid, values == source_values)
        pairs = list(zip(*values))
        functional = all(len({y for x,y in pairs if x==v}) == 1 for v in values[0])
        check("numeric_table_function:"+sid, functional == (sid != TABLES[2]))
        matrices.append({"id":sid,"pairs":pairs,"function":functional})
    lookup = dict(matrices[-1]["pairs"])
    check("lookup_f3_and_inverse1", lookup[3] == 53 and [x for x,y in lookup.items() if y==1] == [2]
          and formula(trees(solution(67))[0]) == "f(x)=1,x=2")
    for number in (69,71,73):
        rule = formula(trees(problem(number))[0]).rstrip(".,").split("=",1)[1]
        answers = list(solution(number).iter("{" + MATH + "}mtd"))
        check("five_numeric_input_answers:"+str(number), len(answers)==5
              and len(list(solution(number).iter("{" + MATH + "}mtr"))) == 1)
        for x, tree in zip(range(-2,3),answers):
            eq = formula(tree).rstrip(";.,").split("=")
            check(f"numeric_answer_input:{number}:{x}",eq[0]==f"f({x})")
            computed, shown = evaluate(rule,{"x":x}),evaluate(eq[-1])
            check(f"numeric_answer_value:{number}:{x}",close(round(computed,3) if number==71 else computed,shown))
        evaluations.append({"exercise":number,"rule":rule,"inputs":list(range(-2,3)),"rounding":3 if number==71 else None})
    rule_nodes=trees(by_id(document,"eip-582"))
    source_rule_nodes=trees(by_id(source,"eip-582"))
    check("source_fgh_rule_order",len(rule_nodes)==3 and [formula(n) for n in rule_nodes]==[formula(n) for n in source_rule_nodes])
    functions={}
    for name,node in zip("fgh",rule_nodes):
        lhs,rhs=formula(node).split("=")
        check("source_fgh_name:"+name,lhs==name+"(x)")
        functions[name]=lambda x,r=rhs:evaluate(r,{"x":x})
    check("fgh_expression74",close(evaluate(formula(trees(problem(74))[0]),functions),-1))
    computed75=evaluate(formula(trees(problem(75))[0]),functions)
    check("fgh_source_answer75",close(computed75,float(text(by_id(document,"fs-id1165134373507")))) and close(computed75,20))
    # The four section rules are actual source MathML, each followed by three domains.
    tech = by_id(source,"fs-id1165134373511")
    domains = []
    active_source = active_rendered = None
    for child in tech:
        if tag(child)=="para" and trees(child):
            active_source=trees(child)[0]
            active_rendered=trees(by_id(document,child.get("id")))[0]
            check("technology_rule_source_bound:"+child.get("id"),formula(active_rendered)==formula(active_source))
        elif tag(child)=="exercise":
            number=source_ex.index(child)+1
            limits=interval(trees(problem(number))[0])
            check("domain_source_bound:"+str(number),limits==interval(trees(problem(number,False))[0]))
            rhs=formula(active_rendered).split("=",1)[1]
            outputs=[evaluate(rhs,{"x":x}) for x in limits]
            if rhs=="(x)^(2)" and limits[0]<=0<=limits[1]:outputs.append(0)
            output_limits=[min(outputs),max(outputs)]
            if len(child)==2:
                actual=interval(trees(solution(number))[0])
                check("source_interval_answer:"+str(number),all(close(a,b) for a,b in zip(actual,output_limits)))
            domains.append({"exercise":number,"rule":rhs,"domain":limits,"computed_range":output_limits,"source_solution":len(child)==2})
    check("12_domains6_supplied_range_answers",len(domains)==12 and sum(r["source_solution"] for r in domains)==6)
    # Explicit original graph observations are bound to unchanged source media and
    # supplied answer direction; raster observations are not analytic proof.
    graph_checks = [(53,0,1), (53,-2,-3), (53,2,-3)]
    graph_answer = [formula(n) for n in trees(solution(53))]
    check("W_graph_supplied_answer",graph_answer==["f(0)=1;","f(x)=-3,x=-2","x=2"])
    check("graph_pixel_notes_bind_points",all(v in by_id(document,"fs-id1165135567425").get("alt") for v in ("(0,1)","(−2,−3)","(2,−3)"))
          and all(v in by_id(document,"fs-id1165135575950").get("alt") for v in ("(−3,4)","(−6,1)","(0,1)","(4,−3)")))
    # Independent transcription of actually inspected coordinate labels and
    # topological features. Approximate raster observations stay approximate.
    image_facts={
        "201":["−2، 0 تے 2","لگ بھگ"], "202":["(0,0)","مثبت","منفی"],
        "203":["x=0","کھبّے","سجّے"], "204":["y=−2","(−1,−2)","(1,2)","y=2"],
        "205":["x=1","x=4","y=−4","y=−2","(1,−3)","(4,−3)","لگ بھگ"],
        "206":["S-ورگا","تصدیق","نہیں"], "207":["(0,3)","(2,−3)","0<x<2","کھُلے","شامل نہیں"],
        "208":["(0,2)","(2,0)"], "209":["(0,0)","X"], "210":["(0,−2)","(1,0)"],
        "211":["(−2,2)","(−4,2)","(0,2)","(−2,4)","(−2,0)"], "212":["1 تے −1","لگ بھگ"],
        "213":["(−2,0)","(−1,1)","(2,2)","(7,3)"], "214":["(0,1)","(−2,−3)","(2,−3)"],
        "215":["(−3,4)","(−6,1)","(0,1)","(4,−3)"],
        "216":["(−2,1)","(−3,1)","(−1,1)","(−2,3)","(−2,−1)","بیضوی"],
        "232":["(1,1)","(0,2)","لگ بھگ","ہموار قطع مکافی نہیں"], "217":["(−2,1)","لگ بھگ","پیچھے ول نہیں"],
        "218":["y=1","x=−1","1/x","درست وضاحت نہیں"], "233":["−π","−π/2","π/2","فنکشن اے، پر اک توں اک نہیں"],
        "220":["y=x²","(−10,100)","(10,100)","[−10,10]"],
        "222":["y=x³","−0.1","0.1","−0.001","0.001","مکعبی"],
        "224":["y=x³","−100","100","−10·10^5","10·10^5","−1,000,000","1,000,000"],
        "226":["y=√x","(0,0)","(100,10)"],
        "228":["y=∛x","−0.001","0.001","−0.1","0.1","مکعب جڑ"],
        "230":["y=∛x","−10·10^5","10·10^5","−1,000,000","1,000,000","−100","100"],
    }
    source_media=[n for n in source.iter() if tag(n)=="media"]
    for original in source_media:
        number=re.search(r"01_01_(\d{3})-",original[0].get("src"))[1]
        actual=by_id(document,original.get("id"))
        check("inspected_graph_features:"+number,all(v in actual.get("alt") for v in image_facts[number]))
    check("26_inspected_graph_feature_sets",len(source_media)==len(image_facts)==26)
    check("million_axis_scaling",10*10**5==1_000_000 and all("10·10^5" in by_id(document,sid).get("alt")
          for sid in ("fs-id1165135434747","fs-id1165135394245")))
    check("soil_supplied_value",formula(trees(solution(89))[0]).rstrip(";.")=="g(5000)=50")
    check("rocket_source_units_values",all(v in text(solution(91)) for v in ("1","200","2","350")))
    final_rule=formula(trees(problem(92))[0]).split("=",1)[1]
    check("final_noninjective_counterexample",close(evaluate(final_rule,{"x":4}),evaluate(final_rule,{"x":6}))
          and close(evaluate(final_rule,{"x":4}),10))
    return {"classification_answers":classifications,"literal_relations":pair_reports,"relation_regressions":analytic,
            "evaluation_answers":evaluations,"tables":matrices,"technology_domains":domains,"graph_observations":graph_checks,
            "inspected_graph_features":image_facts,
            "limits":"Numerical substitution is a regression check, not a universal proof. No absent source solutions are inserted into the reader."}


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


def validate_metadata(document, translation, manifest, check=require):
    check("locale_and_unit", document.attrib == {"lang":"pnb-Arab-PK","dir":"rtl"}
          and translation["locale"]=="pnb-Arab-PK" and translation["unit"]==manifest["unit"]=="PNB-009")
    check("document_structure", [n.tag for n in document]==["head","body"]
          and [n.tag for n in document.find("body")]==["header","main","footer"])
    check("page_container_attributes", all(document.find(p).attrib=={} for p in ("head","body","body/header","body/main")))
    check("page_own_text_tails",pure(document) and pure(document.find("body")))
    head=document.find("head")
    check("head_complete_children",[n.tag for n in head]==["meta","meta","title","style"])
    check("head_metadata_exact",[n.attrib for n in head[:2]]==[{"charset":"utf-8"},{"name":"viewport","content":"width=device-width, initial-scale=1"}])
    check("head_leaf_and_tail_purity",pure(head) and all(len(n)==0 and n.text in (None,"") for n in head[:2]))
    check("head_title_exact",head[2].attrib=={} and len(head[2])==0 and head[2].text==translation["title"]+" — PNB-009")
    check("head_CSS_exact",head[3].attrib=={} and len(head[3])==0 and head[3].text==(BASE/"styles/reader.css").read_text(encoding="utf-8")+UNIT_CSS)
    header=document.find("body/header")
    check("header_complete_order",[n.tag for n in header]==["p","h1","p","p","nav"] and pure(header))
    eyebrow=ET.fromstring('<p class="eyebrow"><bdi dir="ltr">PNB-009 · A30 / m49301</bdi></p>')
    check("header_eyebrow_exact",signature(header[0])==signature(eyebrow))
    check("header_title_subtitle_exact",header[1].attrib==header[2].attrib=={} and len(header[1])==len(header[2])==0
          and header[1].text==translation["title"] and header[2].text==translation["subtitle"])
    status=ET.fromstring('<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی</p>')
    check("header_pending_status_exact",signature(header[3])==signature(status))
    nav=ET.fromstring('<nav aria-label="سبق دے حصے"><a href="unit-008.html">پچھلا سبق</a> · <a href="#para-00001">ماخذ دے مقصد</a> · <a href="#fs-id1165137737761">مشقاں</a> · <a href="#source-glossary-title">ماخذ دیاں اصطلاحاں</a> · <a href="#exercises-bridge">ساڈیاں اصل وضاحتاں</a></nav>')
    check("navigation_exact_text_tails",signature(header[4])==signature(nav))
    footer=by_id(document,"credits")
    check("footer_complete_structure",footer.attrib=={"id":"credits","lang":"en","dir":"ltr"}
          and [n.tag for n in footer]==["h2","p","p","p"] and pure(footer))
    source_url="https://github.com/openstax/osbooks-college-algebra-bundle/blob/"+manifest["commit"]+"/"+manifest["path"]
    credits=[
        '<h2>Sources, credits and changes</h2>',
        '<p>Adapted from <a href="'+source_url+'">OpenStax Precalculus 2e, module m49301</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Figure copyright Rice University, OpenStax, under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Full contributor notices remain in <a href="../provenance/ATTRIBUTION.md">the provenance record</a>. Exact existing image component rows are retained in <a href="../provenance/unit-009-component-notices.json">unit-009-component-notices.json</a>. OpenStax and Rice University do not endorse this adaptation.</p>',
        '<p>Changes: Shahmukhi Punjabi translation of the complete 92-exercise selection, its 46 supplied solutions, five module objectives, module title/metadata and eleven glossary definitions. The other 46 exercises have no supplied solutions in the source. All 26 canonical JPEGs remain unchanged, with faithfully translated source alts retained and separately identified original accessible descriptions. Four placeholder table summaries have disclosed accessible replacements; table order and numbers remain. All 164 source MathML trees reconstruct exactly after 40 reversible terminal period/comma edits, including fourteen owner-bound numeric periods. Internal punctuation, numeric signs, colons, semicolons and superscripts remain. Underlined source emphasis stays underlined. Source circled tokens retain corresponding isolated Latin letters; missing tokens are not invented. Original clarification and bilingual support are separate from source translation.</p>',
        '<p>Indonesian comparison edition: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1. No native-speaker, educator or assistive-technology certification is claimed. This is not a complete textbook, publication or model-training corpus. Module completion requires a separate cross-unit inventory check; the entire five-work assignment remains active.</p>',
    ]
    check("credit_notices_exact",all(signature(n)==signature(ET.fromstring(expected)) for n,expected in zip(footer,credits)))
    with (BASE/"terminology.tsv").open(encoding="utf-8",newline="") as stream:
        terms=list(csv.DictReader(stream,delimiter="\t"))
    ledger='<section id="terminology"><h2>تِن زباناں دی سانجھی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
    ledger+=''.join('<tr><td>'+html.escape(row["pnb-Arab-PK"])+'</td><td lang="ur-Arab-PK">'+html.escape(row["ur-Arab-PK"])+'</td><td lang="en" dir="ltr">'+html.escape(row["en"])+'</td></tr>' for row in terms)
    ledger+='</tbody></table></div></section>'
    check("shared_terminology_complete_structure",signature(by_id(document,"terminology"))==signature(ET.fromstring(ledger)))
    return {"title":translation["title"],"shared_terms":len(terms),"scope":"92 exercises / 46 supplied solutions / metadata / 11 glossary definitions"}


def mutation_tests(document, source, translation, manifest, notices, check):
    tested=[]
    maths=lambda d:list(d.iter("{"+MATH+"}math"))
    contexts=math_contexts(document,source)
    mv=lambda d:validate_math(d,source)
    sv=lambda d:validate_structure(d,source,manifest)
    bv=lambda d:validate_blocks(d,source,translation,manifest)
    tv=lambda d:validate_tables(d,source,translation)
    iv=lambda d:validate_images(d,source,translation,manifest,notices)
    lv=lambda d:validate_links(d,source,manifest)
    av=lambda d:validate_arithmetic(d,source)
    ov=lambda d:validate_bridge(d,source,translation)
    dv=lambda d:validate_directions(d,source)
    meta=lambda d:validate_metadata(d,translation,manifest)
    def reject(name,change,validator,prefix):
        detached=copy.deepcopy(document)
        change(detached)
        try:
            validator(detached)
        except AssertionError as error:
            check("mutation_rejected:"+name,str(error).startswith(prefix))
            tested.append({"mutation":name,"rejection":str(error)})
        else:
            raise AssertionError("mutation_not_rejected:"+name)
    def alter_ledger(d,field,value,context=("fs-id1165137861994/item/2",0)):
        node=maths(d)[contexts.index(context)]
        rows=json.loads(node.get(LEDGER))
        rows[0][field]=value
        if field=="new":at_path(node,rows[0]["path"]).text=value
        node.set(LEDGER,json.dumps(rows))
    reject("changed_first_math_number",lambda d:next(d.iter("{"+MATH+"}mn")).__setattr__("text","999"),mv,"exact_math_reconstruction")
    reject("forged_negative_MN_old",lambda d:alter_ledger(d,"old","3."),mv,"ledger_old_matches_source")
    reject("reversible_negative_sign_removed",lambda d:alter_ledger(d,"new","3"),mv,"ledger_new_matches_policy")
    reject("reversible_MN_value_changed",lambda d:alter_ledger(d,"new","-999"),mv,"ledger_new_matches_policy")
    reject("missing_required_ledger",lambda d:next(n for n in maths(d) if n.get(LEDGER)).attrib.pop(LEDGER),mv,"complete_required_ledger")
    def duplicate_ledger(d):
        node=next(n for n in maths(d) if n.get(LEDGER));rows=json.loads(node.get(LEDGER));rows.append(copy.deepcopy(rows[0]));node.set(LEDGER,json.dumps(rows))
    reject("duplicate_ledger_path",duplicate_ledger,mv,"ledger_unique_path")
    reject("duplicate_ledger_JSON_key",lambda d:next(n for n in maths(d) if n.get(LEDGER)).set(LEDGER,'[{"path":[],"old":"x","old":"y","new":""}]'),mv,"ledger_json_keys_unique")
    reject("ledger_out_of_bounds",lambda d:next(n for n in maths(d) if n.get(LEDGER)).set(LEDGER,'[{"path":[999],"old":".","new":""}]'),mv,"source_position_whitelist")
    def internal_punctuation(d,kind):
        originals=list(source.iter("{"+MATH+"}math"))
        i,path=next((i,path) for i,original in enumerate(originals) for path,node in paths(original)
                    if tag(node)=="mo" and node.text==kind and path not in allowed_edits(original,contexts[i]))
        node=maths(d)[i];at_path(node,path).text="";rows=json.loads(node.get(LEDGER,"[]"));rows.append({"path":list(path),"old":kind,"new":""});node.set(LEDGER,json.dumps(rows))
    for token,label in [(";","semicolon"),(":","colon"),(",","internal_comma")]:
        reject("reversible_"+label,lambda d,t=token:internal_punctuation(d,t),mv,"source_position_whitelist")
    reject("math_wrapper_text",lambda d:parents(d)[maths(d)[0]].__setattr__("text","f(2)=999"),mv,"math_wrapper_pure")
    reject("math_wrapper_extra_child",lambda d:parents(d)[maths(d)[0]].append(ET.fromstring('<b>999</b>')),mv,"math_wrapper_pure")
    reject("math_tree_tail",lambda d:maths(d)[0].__setattr__("tail","h != 0"),mv,"math_wrapper_pure")
    reject("math_hidden_wrapper",lambda d:parents(d)[maths(d)[0]].set("hidden","hidden"),mv,"math_wrapper_attributes")
    reject("math_wrong_owner",lambda d:parents(d)[maths(d)[0]].set("data-source-owner","different"),mv,"math_wrapper_attributes")
    reject("cube_root_degree_changed",lambda d:next(d.iter("{"+MATH+"}mroot"))[1].__setattr__("text","2"),mv,"exact_math_reconstruction")
    reject("square_root_replaced_cube",lambda d:next(d.iter("{"+MATH+"}msqrt")).__setattr__("tag","{"+MATH+"}mroot"),mv,"exact_math_reconstruction")
    reject("unkeyed_source_paragraph",lambda d:by_id(d,SECTION).append(ET.fromstring('<p dir="ltr">f(2)=999; h != 0</p>')),sv,"complete_structural_children")
    reject("source_container_own_text",lambda d:by_id(d,SECTION).__setattr__("text","f(2)=999"),sv,"structural_text_tails")
    reject("source_child_tail",lambda d:by_id(d,SECTION)[0].__setattr__("tail","f(2)=999"),sv,"structural_text_tails")
    reject("main_extra_node",lambda d:d.find("body/main").append(ET.fromstring('<p>999</p>')),sv,"complete_main_topology")
    reject("main_extra_tail",lambda d:d.find("body/main")[1].__setattr__("tail","999"),sv,"main_text_tails")
    reject("source_label_tail",lambda d:d.find("body/main")[1][0].__setattr__("tail"," پورا کم مکمل اے"),sv,"source_label_exact")
    reject("invented_absent_solution",lambda d:by_id(d,manifest["exercise_ids"][1]).append(ET.fromstring('<section class="source-solution"><p>999</p></section>')),sv,"complete_structural_children")
    reject("wrong_local_exercise_number",lambda d:by_id(d,manifest["exercise_ids"][2]).find("h4/bdi").__setattr__("text","999"),sv,"local_heading_exact")
    reject("raw_metadata_UUID_changed",lambda d:marked(d,"data-source-field","uuid")[0].__setattr__("text","invented"),sv,"raw_metadata_field")
    reject("metadata_field_tail",lambda d:marked(d,"data-source-field","content-id")[0].__setattr__("tail"," extra claim"),sv,"raw_metadata_field")
    reject("metadata_extra_paragraph",lambda d:marked(d,"data-source-tag","metadata").append(ET.fromstring('<p>999</p>')),sv,"complete_structural_children")
    reject("glossary_extra_definition",lambda d:marked(d,"class","source-glossary").find("dl").append(ET.fromstring('<div>999</div>')),sv,"glossary11_definitions")
    reject("glossary_heading_tail",lambda d:by_id(d,"source-glossary-title").__setattr__("tail","999"),sv,"glossary_wrapper_exact")
    reject("objective_extra_item",lambda d:by_id(d,"list-00001").append(ET.fromstring('<li>999</li>')),sv,"complete_structural_children")
    reject("source_keyed_condition_injection",lambda d:by_id(d,"fs-id1165137844421").append(ET.fromstring('<bdi dir="ltr">x != 0</bdi>')),bv,"exact_block_fragment")
    reject("source_link_tail_injection",lambda d:by_id(d,"fs-id1165135641701").find("a").__setattr__("tail","999"),bv,"exact_block_fragment")
    reject("source_underlined_not_removed",lambda d:by_id(d,"fs-id1165137844421").find("u").__setattr__("text","اے"),bv,"exact_block_fragment")
    amended=copy.deepcopy(translation);key="fs-id1165137844421"
    amended["source_blocks"][key]=amended["source_blocks"][key].replace('<u>','<em>').replace('</u>','</em>')
    reject("underline_even_if_draft_changed",lambda d:by_id(d,key).find("u").__setattr__("tag","em"),lambda d:validate_blocks(d,source,amended,manifest),"source_emphasis_style")
    unsafe_translation=copy.deepcopy(translation)
    unsafe_key="fs-id1165134373507"
    unsafe_translation["source_blocks"][unsafe_key]=unsafe_translation["source_blocks"][unsafe_key].replace('<bdi dir="ltr">','<bdi dir="ltr" hidden="hidden">')
    reject("hidden_inline_even_if_draft_matches",lambda d:by_id(d,unsafe_key).find("bdi").set("hidden","hidden"),
           lambda d:validate_blocks(d,source,unsafe_translation,manifest),"source_inline_markup_allowlist")
    part_key=next(key for key,n in source_specs(source).items() if any(tag(c)=="span" and c.get("class")=="token" for c in n))
    reject("circled_part_order_changed",lambda d:target_block(d,part_key,source_specs(source)[part_key]).find("span").__setattr__("text","(d)"),bv,"exact_block_fragment")
    mixed_key=next(key for key,n in source_specs(source).items() if tag(n)=="para" and any(tag(c)=="list" for c in n))
    reject("mixed_para_child_tail_injection",lambda d:by_id(d,mixed_key).find("ol").__setattr__("tail","999"),bv,"exact_block_fragment")
    def move_child(d):
        node=by_id(d,mixed_key);child=node.find("ol");child.tail=node.text;node.text=None
    reject("mixed_para_child_order",move_child,bv,"exact_block_fragment")
    newline_key=next(key for key,n in source_specs(source).items() if any(tag(c)=="newline" for c in n))
    reject("source_newline_removed",lambda d:by_id(d,newline_key).remove(by_id(d,newline_key).find("br")),bv,"exact_block_fragment")
    reject("numeric_table_cell_changed",lambda d:reader_rows(by_id(d,TABLES[0]))[1][1].__setattr__("text","999"),tv,"table_data_exact")
    reject("duplicate_input_erased",lambda d:reader_rows(by_id(d,TABLES[2]))[0][3].__setattr__("text","15"),av,"numeric_table_source_values")
    def swap_rows(d):
        body=by_id(d,TABLES[0]).find("tbody");first=body[0];body.remove(first);body.append(first)
    reject("table_rows_swapped",swap_rows,tv,"table_cell_semantics")
    reject("table_body_orientation",lambda d:by_id(d,TABLES[0]).find("tbody").__setattr__("tag","thead"),tv,"table_exact_child_groups")
    reject("table_header_demoted",lambda d:reader_rows(by_id(d,TABLES[0]))[0][0].__setattr__("tag","td"),tv,"table_cell_semantics")
    reject("table_data_promoted_header",lambda d:reader_rows(by_id(d,TABLES[0]))[0][1].__setattr__("tag","th"),tv,"table_cell_semantics")
    reject("table_colspec_changed",lambda d:by_id(d,TABLES[0]).find("colgroup")[0].set("data-source-colnum","999"),tv,"source_colspec")
    reject("invented_11col_colspec",lambda d:by_id(d,TABLES[3]).insert(0,ET.Element("colgroup")),tv,"table_exact_child_groups")
    reject("invented_unnumbered_caption",lambda d:by_id(d,TABLES[0]).append(ET.fromstring('<caption>15</caption>')),tv,"table_exact_child_groups")
    reject("summary_dots_used_as_ARIA",lambda d:by_id(d,TABLES[0]).set("aria-label",".."),tv,"table_exact_attributes")
    reject("summary_original_label_erased",lambda d:by_id(d,TABLES[0]).attrib.pop("data-description-origin"),tv,"table_exact_attributes")
    reject("table_numeric_tail",lambda d:reader_rows(by_id(d,TABLES[0]))[0][1].__setattr__("tail","999"),tv,"table_row_shape")
    reject("table_scroll_hidden",lambda d:parents(d)[by_id(d,TABLES[0])].set("hidden","hidden"),tv,"table_scroll_wrapper")
    reject("table_advisory_link_tail",lambda d:parents(d)[parents(d)[by_id(d,TABLES[0])]][1][0].__setattr__("tail","999"),tv,"table_advisory_exact")
    first=manifest["images"][0]["media_id"]
    reject("wrong_existing_image",lambda d:by_id(d,first).set("src","../"+manifest["images"][1]["path"]),iv,"image_exact_attributes")
    reject("image_dimension_changed",lambda d:by_id(d,first).set("width","999"),iv,"image_exact_attributes")
    reject("image_source_alt_corrected_silently",lambda d:by_id(d,first).set("data-source-alt",translation["image_alt_overrides"][first]),iv,"image_exact_attributes")
    reject("image_original_mislabeled_source",lambda d:by_id(d,first).set("data-description-origin","source"),iv,"image_exact_attributes")
    reject("image_note_wrong_existing_target",lambda d:by_id(d,first).set("aria-describedby","exercises-domains"),iv,"image_exact_attributes")
    reject("image_hidden",lambda d:by_id(d,first).set("hidden","hidden"),iv,"image_exact_attributes")
    reject("image_wrapper_own_text",lambda d:parents(d)[by_id(d,first)].__setattr__("text","999"),iv,"image_focus_wrapper")
    reject("image_container_own_text",lambda d:parents(d)[parents(d)[by_id(d,first)]].__setattr__("text","999"),iv,"media_container_pure")
    reject("image_advisory_tail",lambda d:parents(d)[parents(d)[by_id(d,first)]][-1][0].__setattr__("tail","999"),iv,"image_advisory_exact")
    altered_notices=copy.deepcopy(notices);altered_notices[0]["attribution"]="Someone else"
    reject("notice_credit_changed",lambda d:None,lambda d:validate_images(d,source,translation,manifest,altered_notices),"exact_existing_whole_notice")
    altered_manifest=copy.deepcopy(manifest);altered_manifest["images"][0]["figure_id"]="invented"
    reject("invented_figure_ID",lambda d:None,lambda d:validate_images(d,source,translation,altered_manifest,notices),"actual_direct_media_no_figure_ID")
    reject("wrong_existing_source_link",lambda d:by_id(d,"fs-id1165135641701").find("a").set("href","#"+TABLES[0]),lv,"one_exact_source_link")
    reject("wrong_link_label",lambda d:by_id(d,"fs-id1165135641701").find("a/bdi").__setattr__("text","1.1.16"),lv,"one_exact_source_link")
    reject("wrong_link_marker",lambda d:by_id(d,"fs-id1165135641701").find("a").set("data-source-link","wrong"),lv,"one_exact_source_link")
    polarity_node=list(by_id(document,"fs-id1165135318977"))[1].get("id")
    reject("supplied_polarity_reversed",lambda d:by_id(d,polarity_node).__setattr__("text","فنکشن نہیں"),av,"supplied_answer_polarity")
    reject("source_plain_answer20_changed",lambda d:by_id(d,"fs-id1165134373507").find("bdi").__setattr__("text","21"),av,"fgh_source_answer75")
    reject("graph207_open_endpoints_closed",lambda d:by_id(d,"fs-id1165135704896").set("alt",by_id(d,"fs-id1165135704896").get("alt").replace("کھُلے","بند")),av,"inspected_graph_features")
    reject("graph205_wrong_Indonesian_alt_endpoint",lambda d:by_id(d,"fs-id1165135386387").set("alt",by_id(d,"fs-id1165135386387").get("alt").replace("x=4","x=5")),av,"inspected_graph_features")
    reject("graph216_ellipse_top_changed",lambda d:by_id(d,"fs-id1165135541720").set("alt",by_id(d,"fs-id1165135541720").get("alt").replace("(−2,3)","(−2,2)")),av,"inspected_graph_features")
    reject("graph233_wrong_injective_claim",lambda d:by_id(d,"fs-id1165135457089").set("alt",by_id(d,"fs-id1165135457089").get("alt").replace("فنکشن اے، پر اک توں اک نہیں","اک توں اک فنکشن اے")),av,"inspected_graph_features")
    reject("original_rounding_note_changed",lambda d:by_id(d,"exercises-rounded-equality").find("bdi").__setattr__("text","4.415"),ov,"original_fragment_exact")
    def move_original(d):
        node=by_id(d,"exercises-bridge");parents(d)[node].remove(node);by_id(d,SECTION).append(node)
    reject("original_notes_inside_source",move_original,ov,"original_separate_from_source")
    reject("body_LTR",lambda d:d.find("body").set("dir","ltr"),dv,"source_prose_RTL")
    reject("numeric_cell_RTL",lambda d:reader_rows(by_id(d,TABLES[0]))[0][1].set("dir","rtl"),dv,"visible_Latin_digits_LTR")
    reject("head_script_injection",lambda d:d.find("head").append(ET.Element("script")),meta,"head_complete_children")
    reject("head_title_tail",lambda d:d.find("head/title").__setattr__("tail","999"),meta,"head_leaf_and_tail_purity")
    reject("metadata_hidden_child",lambda d:d.find("head/meta").append(ET.Element("script")),meta,"head_leaf_and_tail_purity")
    reject("CSS_hidden_source",lambda d:d.find("head/style").__setattr__("text",d.find("head/style").text+"main{display:none}"),meta,"head_CSS_exact")
    reject("header_own_text",lambda d:d.find("body/header").__setattr__("text","999"),meta,"header_complete_order")
    reject("header_title_tail",lambda d:d.find("body/header/h1").__setattr__("tail","999"),meta,"header_complete_order")
    reject("eyebrow_hidden",lambda d:d.find("body/header/p/bdi").set("hidden","hidden"),meta,"header_eyebrow_exact")
    reject("navigation_tail",lambda d:d.find("body/header/nav/a").__setattr__("tail","999"),meta,"navigation_exact_text_tails")
    reject("credit_license_tail_claim",lambda d:by_id(d,"credits")[1][1].__setattr__("tail"," Public domain; obligations waived."),meta,"credit_notices_exact")
    reject("credit_native_certification",lambda d:by_id(d,"credits")[-1].append(ET.fromstring('<span>Native review passed.</span>')),meta,"credit_notices_exact")
    reject("terminology_extra_claim",lambda d:by_id(d,"terminology").append(ET.fromstring('<p>999</p>')),meta,"shared_terminology_complete_structure")
    reject("terminology_cell_tail",lambda d:by_id(d,"terminology").find("div/table/tbody/tr/td").__setattr__("tail","999"),meta,"shared_terminology_complete_structure")
    reject("bidi_control",lambda d:by_id(d,"fs-id1165137844421").__setattr__("text","\u202e"),validate_unicode,"reader_unicode_gate")
    # These preparation checks call only pure validators; never prepare()/write.
    from prepare_unit_009 import validate_declared_images, validate_selection
    validate_declared_images(source,manifest["images"])
    full=ET.parse(ROOT/manifest["source_byte_witnesses"]["canonical_checkout_path"]).getroot()
    validate_selection(source,full,manifest)
    def preparation_reject(name,change,selection=False):
        selected,specs=copy.deepcopy(source),copy.deepcopy(manifest["images"])
        change(selected,specs)
        try:
            validate_selection(selected,full,manifest) if selection else validate_declared_images(selected,specs)
        except AssertionError:
            check("mutation_rejected:"+name,True)
            tested.append({"mutation":name,"rejection":"pure_preparation_validation"})
        else:
            raise AssertionError("preparation_mutation_not_rejected:"+name)
    preparation_reject("preparation_parent_traversal",lambda s,rows:rows[0].__setitem__("path","../elsewhere.jpg"))
    preparation_reject("preparation_backslash_path",lambda s,rows:rows[0].__setitem__("path","assets\\image.jpg"))
    preparation_reject("preparation_absolute_path",lambda s,rows:rows[0].__setitem__("path","C:/image.jpg"))
    preparation_reject("preparation_source_path_changed",lambda s,rows:rows[0].__setitem__("source_path",rows[1]["source_path"]))
    preparation_reject("preparation_duplicate_asset",lambda s,rows:rows[0].__setitem__("path",rows[1]["path"]))
    preparation_reject("preparation_missing_media",lambda s,rows:rows.pop())
    preparation_reject("preparation_invented_figure",lambda s,rows:rows[0].__setitem__("figure_id","invented"))
    preparation_reject("preparation_source_alt_changed",lambda s,rows:rows[0].__setitem__("source_alt","invented"))
    preparation_reject("preparation_boolean_dimension",lambda s,rows:rows[0].__setitem__("width",True))
    preparation_reject("preparation_root_component_omitted",lambda s,rows:s.remove(s[0]),True)
    preparation_reject("preparation_glossary_definition_omitted",lambda s,rows:s[3].remove(s[3][-1]),True)
    preparation_reject("preparation_source_tail_changed",lambda s,rows:s[2][0].__setattr__("tail","omission"),True)
    raw=READER.read_text(encoding="utf-8")
    for name,altered in [("reader_prelude_script",'<script>document.body.remove()</script>'+raw),
                         ("reader_trailing_claim",raw+'<p>All source answers are supplied.</p>'),
                         ("reader_omitted_doctype",raw.removeprefix('<!doctype html>\n'))]:
        try:
            validate_envelope(altered)
        except AssertionError as error:
            check("mutation_rejected:"+name,str(error)=="exact_reader_envelope")
            tested.append({"mutation":name,"rejection":str(error)})
        else:
            raise AssertionError("reader_envelope_mutation_not_rejected:"+name)
    return tested


def input_paths(manifest):
    local=["source-excerpts/manifest-009.json","source-excerpts/unit-009.cnxml","translations/unit-009.json",
           "qa/unit-009-language-notes.md","provenance/unit-009-component-notices.json","provenance/ATTRIBUTION.md",
           "styles/reader.css","terminology.tsv","scripts/build_exercises.py","scripts/prepare_unit_009.py",
           "scripts/qa_notation.py","scripts/qa_exercises.py","reader/unit-008.html"]
    result=[BASE/p for p in local]
    result.extend(BASE/"canon/receipts"/name for name in RECEIPTS)
    for spec in manifest["images"]:
        result.extend([BASE/spec["path"],ROOT/"downloads/complete-upstream/osbooks-college-algebra-bundle"/spec["source_path"],
                       ROOT/"downloads/extracted/A30/repo/source"/spec["source_path"]])
    result.extend(ROOT/manifest["source_byte_witnesses"][k] for k in ("canonical_checkout_path","pinned_lf_witness_path","comparison_path"))
    result.extend([ROOT/manifest["next_collection_module"]["collection_path"],ROOT/"downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv"])
    return list(dict.fromkeys(result))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit",choices=["009"],default="009")
    parser.add_argument("--check-only",action="store_true",help="Read-only check of existing reader; no builds or receipt writes")
    arguments=parser.parse_args()
    def load(path):return json.loads((BASE/path).read_text(encoding="utf-8"),object_pairs_hook=unique_object)
    manifest,translation,notices=load("source-excerpts/manifest-009.json"),load("translations/unit-009.json"),load("provenance/unit-009-component-notices.json")
    source=ET.parse(BASE/"source-excerpts/unit-009.cnxml").getroot()
    inputs=input_paths(manifest)
    before={p.relative_to(ROOT).as_posix():sha256(p) for p in inputs}
    if not arguments.check_only:
        subprocess.run([sys.executable,"-B",str(BASE/"scripts/prepare_unit_009.py"),"--check-only"],check=True)
        command=[sys.executable,"-B",str(BASE/"scripts/build_exercises.py"),"--unit","009"]
        subprocess.run(command,check=True);first=READER.read_bytes();subprocess.run(command,check=True)
        require("two_reader_builds_identical",READER.read_bytes()==first)
    document=parse_reader(READER.read_text(encoding="utf-8"))
    checks=[]
    def check(name,condition):
        require(name,condition);checks.append(name)
    validate_envelope(READER.read_text(encoding="utf-8"),check)
    for path in inputs:
        if path.is_relative_to(BASE) and path.suffix in (".json",".cnxml",".md",".py",".css",".tsv",".html"):
            check("Unicode_input:"+path.relative_to(BASE).as_posix(),FORBIDDEN.search(path.read_text(encoding="utf-8")) is None)
    validate_unicode(document,check)
    report={"unit":"PNB-009","boundary":validate_boundary(source,manifest,check),
        "structure":validate_structure(document,source,manifest,check),"blocks":validate_blocks(document,source,translation,manifest,check),
        "math":validate_math(document,source,check),"tables":validate_tables(document,source,translation,check),
        "images":validate_images(document,source,translation,manifest,notices,check),"links":validate_links(document,source,manifest,check),
        "arithmetic":validate_arithmetic(document,source,check),"original_bridge":validate_bridge(document,source,translation,check),
        "metadata":validate_metadata(document,translation,manifest,check)}
    validate_directions(document,source,check)
    report["mutations"]=mutation_tests(document,source,translation,manifest,notices,check)
    check("inputs_stable_during_run",before=={p.relative_to(ROOT).as_posix():sha256(p) for p in inputs})
    report.update({"checks_passed":len(checks),"checks":checks,"mutation_count":len(report["mutations"]),"inputs_sha256":before,
                   "reader_sha256":sha256(READER),"two_builds_byte_identical":not arguments.check_only,"canon_receipts":RECEIPTS,
                   "normalization":"CNXML digests alone use CRLF-to-LF equivalence; raw canonical/comparison digests are separately checked.",
                   "limits":["No module-completion claim until independent cross-unit inventory; entire five-work assignment remains active.",
                             "Structural/source/math QA is not native Punjabi, educator, visual or assistive-technology certification.",
                             "Only 46 of 92 exercises have source solutions. No new answers are inserted into the source translation.",
                             "Graph observations come from inspected, pinned pixels and cannot certify an exact formula from a generic raster."]})
    if not arguments.check_only:
        (BASE/"qa/structural-009.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"PNB-009: {len(checks)} checks passed; {len(report['mutations'])} detached mutations; {len(report['math']['edits'])} reversible MathML edits")


if __name__=="__main__":
    main()
