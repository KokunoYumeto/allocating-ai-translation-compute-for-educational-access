"""Independent source-bound PNB-008 QA; adversaries mutate detached DOMs only."""
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
READER = BASE / "reader/unit-008.html"
CNXML = "http://cnx.rice.edu/cnxml"
SELECTED = ["fs-id1165135422920", "fs-id1165135435781", "fs-id1165137610952",
            "fs-id1165135545919", "fs-id1165135203679", "fs-id1165137692068"]
NEXT = "fs-id1165137737761"
TABLES = ["Table_01_01_13", "Table_01_01_14", "eip-id1165134393730"]
SPECIAL_EDGES = {("fs-id1165137637786", 9): ("mn", "1.", "1"),
                 ("fs-id1165137761111", 0): ("mo", "?", "")}
RECEIPTS = ["PNB-008-next-unit-20260831T001753181082Z.json",
            "PNB-008-draft-20260831T002617605563Z.json",
            "PNB-008-revision-20260831T004917231179Z.json",
            "PNB-008-qa-20260831T005512298908Z.json"]
PIXEL_PAIRS = [
    [(-2, 2), (0, 2), (2, 2)],
    [(-2, -2), (0, 0), (2, 2)],
    [(-2, 2), (0, 0), (2, 2)],
    [(-2, 4), (-1, 1), (0, 0), (1, 1), (2, 4)],
    [(-1, -1), (-0.5, -0.125), (0, 0), (0.5, 0.125), (1, 1)],
    [(-2, -0.5), (-1, -1), (-0.5, -2), (0.5, 2), (1, 1), (2, 0.5)],
    [(-2, 0.25), (-1, 1), (-0.5, 4), (0.5, 4), (1, 1), (2, 0.25)],
    [(0, 0), (1, 1), (4, 2)],
    [(-1, -1), (-0.125, -0.5), (0, 0), (0.125, 0.5), (1, 1)],
]


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
    data = path.read_bytes()
    if path.suffix == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def parents(node):
    return {child: owner for owner in node.iter() for child in owner}


def by_id(root, identifier):
    found = [node for node in root.iter() if node.get("id") == identifier]
    require("unique_id:" + identifier, len(found) == 1)
    return found[0]


def parse_reader(raw):
    return ET.fromstring(raw[raw.index("<html"):])


def content_signature(node):
    return node.text, tuple((signature(child), child.tail) for child in node)


def pure(node):
    return node.text in (None, "") and all(child.tail in (None, "") for child in node)


def source_rows(table):
    return [node for node in table.iter() if tag(node) == "row"]


def reader_rows(table):
    return [row for group in table if group.tag in ("thead", "tbody") for row in group]


def own_math(node):
    result = []
    for child in node:
        if tag(child) == "math":
            result.append(child)
        elif tag(child) not in ("media", "table", "figure", "list", "para"):
            result.extend(own_math(child))
    return result


def own_prose(node):
    result = node.text or ""
    for child in node:
        if tag(child) not in ("math", "link", "media", "table", "figure"):
            result += own_prose(child)
        result += child.tail or ""
    return result


def source_specs(source):
    """Derive text owners, including formula cells but excluding pure media cells."""
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
                for ci, entry in enumerate(row, 1):
                    is_media = len(entry) == 1 and tag(entry[0]) == "media"
                    # Actual letter-grade symbols are data, unlike the two headings.
                    is_grade_data = sid == TABLES[0] and ri > 1
                    if not is_media and not is_grade_data:
                        result[f"{sid}/row/{ri}/entry/{ci}"] = entry
            for media in (n for n in node.iter() if tag(n) == "media"):
                visit(media)
            return
        if name in ("title", "para", "label", "item"):
            key = (f'{owner.get("id")}/item/{index + 1}' if name == "item"
                   else node.get("id") or f'{owner.get("id")}/{name}')
            result[key] = node
            return
        for position, child in enumerate(node):
            visit(child, node, position)

    visit(source)
    return result


def target_block(document, source, key, original):
    if tag(original) == "entry":
        table, _, row, _, column = key.split("/")
        return reader_rows(by_id(document, table))[int(row) - 1][int(column) - 1]
    if original.get("id"):
        return by_id(document, original.get("id"))
    owner = parents(source)[original]
    target = by_id(document, owner.get("id"))
    if tag(original) == "item":
        return target.findall("li")[list(owner).index(original)]
    name = "h2" if tag(original) == "title" and tag(owner) == "section" else "h3"
    require("one_source_heading:" + key, len(target.findall(name)) == 1)
    return target.find(name)


def validate_boundary(source, manifest, check=require):
    witnesses = manifest["source_byte_witnesses"]
    canonical = ROOT / witnesses["canonical_checkout_path"]
    pinned = ROOT / witnesses["pinned_lf_witness_path"]
    comparison = ROOT / witnesses["comparison_path"]
    check("canonical_checkout_sha", hashlib.sha256(canonical.read_bytes()).hexdigest()
          == witnesses["canonical_checkout_sha256"] == "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612")
    check("pinned_module_sha", sha256(pinned) == manifest["full_module_sha256"]
          == "81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3")
    check("only_CRLF_normalized", canonical.read_bytes().replace(b"\r\n", b"\n") == pinned.read_bytes())
    check("Indonesian_comparison_sha", hashlib.sha256(comparison.read_bytes()).hexdigest()
          == witnesses["comparison_sha256"] == "67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a")
    full = ET.parse(pinned).getroot()
    originals = [by_id(full, sid) for sid in SELECTED]
    p = parents(full)
    content = p[originals[0]]
    check("six_contiguous_complete_content_children", all(p[n] is content for n in originals)
          and list(content)[3:9] == originals and list(content)[9].get("id") == NEXT)
    check("six_subtree_witnesses_and_tails", len(source) == 6 and all(
        signature(left) == signature(right) and left.tail == right.tail
        for left, right in zip(source, originals)))
    check("selection_manifest", manifest["selection_ids"] == SELECTED and manifest["next_source_id"] == NEXT
          and manifest["commit"] == "789b54099106b071d1d32bfcee454fed72eb4768")
    check("selection_wrapper", source.attrib == {"id": "m49301-unit-008-excerpt"} and tag(source) == "document")
    check("selection_boundary_rows", manifest["selection_boundary"]["included_direct_children"] == [
        {"index": i + 4, "tag": "section", "id": sid, "coverage": "complete subtree"}
        for i, sid in enumerate(SELECTED)])
    check("source_excerpt_digest", sha256(BASE / "source-excerpts/unit-008.cnxml") == manifest["excerpt_sha256"])
    return {"selected": SELECTED, "next_source_id": NEXT, "complete_subtrees": 6}


def validate_structure(document, source, check=require):
    source_ids = [n.get("id") for n in source.iter() if n is not source and n.get("id")]
    ids = [n.get("id") for n in document.iter() if n.get("id")]
    check("99_source_identifiers", len(source_ids) == 99 and len(set(source_ids)) == 99)
    check("reader_all_ids_unique", len(ids) == len(set(ids)))
    check("source_ids_exact_order", [sid for sid in ids if sid in source_ids] == source_ids)
    check("no_excerpt_wrapper_or_next_section", source.get("id") not in ids and NEXT not in ids)
    op, rp = parents(source), parents(document)

    def lineage(node, mapping):
        result = []
        while node in mapping:
            node = mapping[node]
            if node.get("id") in source_ids:
                result.append(node.get("id"))
        return result

    check("all99_source_ancestries", all(lineage(n, op) == lineage(by_id(document, n.get("id")), rp)
          for n in source.iter() if n is not source and n.get("id")))
    main = document.find("body/main")
    expected_main = [("aside", "toolkit-source-context"), ("p", None),
                     *[("section", sid) for sid in SELECTED],
                     ("section", "toolkit-bridge"), ("section", "terminology")]
    check("complete_main_topology", [(n.tag, n.get("id")) for n in main] == expected_main)
    check("main_text_tails", not (main.text or "").strip() and all(not (n.tail or "").strip() for n in main))
    check("source_label_slot", main[1].attrib == {"class": "source-label"})
    source_label = ET.fromstring('<p class="source-label">ماخذ دا ترجمہ: <bdi dir="ltr" lang="en">OpenStax Precalculus 2e, §1.1</bdi> دا چُنیا ہویا حصہ؛ پورے حصے دا ترجمہ نہیں۔</p>')
    check("source_label_exact", signature(main[1]) == signature(source_label))
    structural = {"section", "example", "exercise", "problem", "solution", "note", "list", "figure"}

    def output_tag(node, owner):
        name = tag(node)
        if name == "list":
            return "ol" if node.get("list-type") == "enumerated" else "ul"
        if name == "title":
            return "h2" if tag(owner) == "section" else "h3"
        return {"section": "section", "example": "section", "exercise": "div", "problem": "div",
                "solution": "section", "note": "aside", "figure": "figure", "para": "p",
                "label": "h3", "item": "li", "table": "div", "media": "div"}[name]

    for original in (n for n in source.iter() if tag(n) in structural):
        sid, name = original.get("id"), tag(original)
        target = by_id(document, sid)
        attrs = {"id": sid}
        if name == "section":
            attrs["class"] = "translated"
        elif name in ("example", "exercise", "problem", "solution"):
            attrs["class"] = "source-" + name
        elif name == "list" and any(c.get("class") == "token" for item in original for c in item):
            attrs.update({"class": "source-parts", "role": "list"})
        check("container_tag_attributes:" + sid, target.tag == output_tag(original, op[original]) and target.attrib == attrs)
        expected = []
        if name in ("example", "solution"):
            heading_tag = "h2" if name == "example" else "h3"
            expected.append((heading_tag, None, None))
            label = (f'<h2>حل کیتی مثال <bdi dir="ltr">{int(sid.rsplit("_", 1)[1])}</bdi></h2>'
                     if name == "example" else "<h3>حل</h3>")
            check("generated_heading:" + sid, signature(target[0]) == signature(ET.fromstring(label)))
        for child in original:
            kind = tag(child)
            expected.append((output_tag(child, original), None if kind in ("table", "media") else child.get("id"),
                             child.get("id") if kind in ("table", "media") else None))
        check("complete_structural_children:" + sid,
              [(n.tag, n.get("id"), n.get("data-source-child")) for n in target] == expected)
        check("no_structural_text_or_tails:" + sid, pure(target))
        check("source_container_has_no_omitted_prose:" + sid, not (original.text or "").strip()
              and all(not (n.tail or "").strip() for n in original))
    examples = [n.get("id") for n in source.iter() if tag(n) == "example"]
    check("three_examples13_14_15", examples == [f"Example_01_01_{i}" for i in range(13, 16)])
    pairings = []
    for exercise in (n for n in source.iter() if tag(n) == "exercise"):
        sequence = [(tag(n), n.get("id")) for n in exercise]
        target = by_id(document, exercise.get("id"))
        check("paired_problem_solution:" + exercise.get("id"), [kind for kind, _ in sequence] == ["problem", "solution"]
              and [(n.get("class").removeprefix("source-"), n.get("id")) for n in target] == sequence)
        pairings.append({"exercise": exercise.get("id"), "children": sequence})
    check("seven_complete_pairs", len(pairings) == 7)
    check("no_footnotes_or_equations", not any(tag(n) in ("footnote", "equation") for n in source.iter())
          and not any(n.get("class") in ("source-endnotes", "equation") for n in document.iter()))
    return {"source_ids": source_ids, "pairings": pairings}


def validate_blocks(document, source, translation, check=require):
    specs = source_specs(source)
    blocks = translation["source_blocks"]
    check("133_source_keys_in_order", len(specs) == len(blocks) == 133 and list(specs) == list(blocks))
    totals = {"math": 0, "link": 0, "child": 0, "newlines": 0, "parts": 0, "emphasis": 0}
    numerals = {}
    for key, original in specs.items():
        target = target_block(document, source, key, original)
        value, name = blocks[key], tag(original)
        if name in ("table", "media"):
            attribute = "data-source-summary" if name == "table" else "data-source-alt"
            check("faithful_source_attribute:" + key, target.get(attribute) == value)
            source_text, translated_text = original.get("summary" if name == "table" else "alt"), value
        else:
            if name != "entry":
                p = parents(source)[original]
                expected_tag = {"para": "p", "item": "li", "label": "h3",
                                "title": "h2" if tag(p) == "section" else "h3"}[name]
                check("block_tag_attributes:" + key, target.tag == expected_tag
                      and target.attrib == ({"id": original.get("id")} if original.get("id") else {}))
            maths = own_math(original)
            links = [c for c in original if tag(c) == "link"]
            for kind, nodes in (("math", maths), ("link", links), ("child", [])):
                check(f"ordered_{kind}_slots:{key}", re.findall(r"\{\{" + kind + r":(\d+)\}\}", value)
                      == [str(i) for i in range(len(nodes))])
                totals[kind] += len(nodes)
            expected = ET.fromstring("<fragment>" + re.sub(
                r"\{\{(math|link):(\d+)\}\}", r'<slot kind="\1" index="\2" />', value) + "</fragment>")
            actual, counts = copy.deepcopy(target), {"math": 0, "link": 0}

            def slots(node):
                for index, child in enumerate(list(node)):
                    kind = "math" if child.get("class") == "math-isolate" else "link" if child.tag == "a" else None
                    if kind:
                        replacement = ET.Element("slot", {"kind": kind, "index": str(counts[kind])})
                        counts[kind] += 1
                        replacement.tail = child.tail
                        node.remove(child)
                        node.insert(index, replacement)
                    else:
                        slots(child)

            slots(actual)
            check("exact_block_fragment:" + key, content_signature(actual) == content_signature(expected))
            check("actual_math_link_counts:" + key, counts == {"math": len(maths), "link": len(links)})
            clean = ET.fromstring("<fragment>" + re.sub(r"\{\{(?:math|link):\d+\}\}", "", value) + "</fragment>")
            check("source_inline_term_ids:" + key, [n.get("id") for n in clean.iter() if n.get("id")]
                  == [n.get("id") for n in original.iter() if tag(n) == "term"])
            emphasis = ["em" if n.get("effect") == "italics" else "strong" for n in original if tag(n) == "emphasis"]
            check("source_emphasis_style:" + key, [n.tag for n in target if n.tag in ("em", "strong")] == emphasis)
            totals["emphasis"] += len(emphasis)
            newlines = [n for n in original if tag(n) == "newline"]
            check("source_newlines:" + key, len(target.findall("br")) == len(newlines))
            totals["newlines"] += len(newlines)
            tokens = [n.text for n in original if tag(n) == "span" and n.get("class") == "token"]
            labels = [n for n in target if n.get("class") == "part-label"]
            check("source_part_correspondence:" + key, len(labels) == len(tokens) and all(
                n.tag == "span" and n.attrib == {"class": "part-label", "dir": "ltr"} and len(n) == 0
                and n.text == "(" + chr(ord("a") + "ⓐⓑⓒⓓ".index(token)) + ")"
                for n, token in zip(labels, tokens)))
            totals["parts"] += len(tokens)
            source_text, translated_text = own_prose(original), text(clean)
        digits = re.findall(r"\d+(?:\.\d+)?", source_text)
        check("plain_source_numbers:" + key, re.findall(r"\d+(?:\.\d+)?", translated_text) == digits)
        if digits:
            numerals[key] = digits
    check("all_block_slot_totals", totals == {"math": 49, "link": 37, "child": 0,
          "newlines": 2, "parts": 10, "emphasis": 13})
    return {"keys": list(specs), "slots": totals, "plain_numbers": numerals}


def math_contexts(document, source, rendered=False):
    specs = source_specs(source)
    owners = {(target_block(document, source, key, node) if rendered else node): key
              for key, node in specs.items() if tag(node) not in ("table", "media")}
    root = document if rendered else source
    p, result, counts = parents(root), [], {}
    for math_node in root.iter("{" + MATH + "}math"):
        node = math_node
        while node in p:
            node = p[node]
            if node in owners:
                key = owners[node]
                result.append((key, counts.get(key, 0)))
                counts[key] = counts.get(key, 0) + 1
                break
        else:
            raise AssertionError("math_has_actual_source_owner")
    return result


def permitted_edits(original, context):
    leaves = [(path, node) for path, node in paths(original) if not len(node)]
    allowed = {}
    for path, leaf in reversed(leaves):
        if tag(leaf) == "mo" and leaf.text in (".", ","):
            allowed[path] = (leaf.text, "")
        else:
            break
    if context in SPECIAL_EDGES:
        path, leaf = leaves[-1]
        kind, before, after = SPECIAL_EDGES[context]
        require("exact_special_source_position:" + str(context), tag(leaf) == kind and leaf.text == before)
        if kind == "mn":
            require("terminal_numeric_semantics", re.fullmatch(r"[0-9]+\.", before) is not None
                    and float(before) == float(after))
        allowed[path] = (before, after)
    return allowed


def restore_math(original, rendered, context, check=require):
    label = str(context)
    check("math_root_ltr:" + label, rendered.get("dir") == "ltr")
    raw = rendered.get(LEDGER)
    try:
        entries = [] if raw is None else json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise AssertionError("ledger_JSON") from error
    check("ledger_nonempty_if_present:" + label, isinstance(entries, list) and (raw is None or bool(entries)))
    allowed, restored, seen = permitted_edits(original, context), copy.deepcopy(rendered), set()
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
    check("49_exact_namespace_math_trees", len(originals) == len(actual) == 49
          and all(n.tag == "{" + MATH + "}math" for n in actual))
    contexts = math_contexts(document, source)
    check("49_exact_math_owners_and_slots", contexts == math_contexts(document, source, True))
    p, edits = parents(document), []
    for index, (left, right, context) in enumerate(zip(originals, actual, contexts)):
        wrapper = p[right]
        check(f"math_wrapper_attributes:{index}", wrapper.tag == "span"
              and wrapper.attrib == {"class": "math-isolate", "dir": "ltr"})
        check(f"math_wrapper_pure:{index}", len(wrapper) == 1 and wrapper[0] is right and pure(wrapper))
        entries = restore_math(left, right, context, check)
        edits.extend({"tree": index, "owner": context[0], "slot": context[1], **entry} for entry in entries)
    check("ledgers_only_on_source_math", all(n in actual for n in document.iter() if LEDGER in n.attrib))
    check("no_new_display_math", not any(n.get("display") for n in actual))
    check("two_exact_special_edge_owners", set(SPECIAL_EDGES).issubset(contexts))
    check("source_counted_edits", len(edits) == sum(len(permitted_edits(n, c)) for n, c in zip(originals, contexts)))
    check("20_toolkit_formula_trees", sum("/entry/" in key for key, _ in contexts) == 20)
    return {"trees": 49, "contexts": contexts, "edits": edits, "special_edges": [
        {"owner": k[0], "slot": k[1], "tag": v[0], "old": v[1], "new": v[2]} for k, v in SPECIAL_EDGES.items()]}


def validate_tables(document, source, translation, check=require):
    originals = [n for n in source.iter() if tag(n) == "table"]
    check("three_table_IDs", [n.get("id") for n in originals] == TABLES)
    check("only_three_source_tables", len([n for n in document.iter("table") if n.get("class") == "source-table"]) == 3)
    data_keys = [f"{table.get('id')}/row/{ri}/entry/{ci}"
                 for table in originals for ri, row in enumerate(source_rows(table), 1)
                 for ci, entry in enumerate(row, 1) if own_math(entry)]
    check("18_translated_formula_data_cells", len(data_keys) == 18 and translation["translated_table_data_cells"] == data_keys)
    check("two_summary_overrides", set(translation["table_summary_overrides"]) == set(TABLES[1:]))
    op, rp, report = parents(source), parents(document), []
    for original in originals:
        sid, target = original.get("id"), by_id(document, original.get("id"))
        group = next(n for n in original if tag(n) == "tgroup")
        columns = [n for n in group if tag(n) == "colspec"]
        summary = translation["source_blocks"][sid + "/summary"]
        override = sid in translation["table_summary_overrides"]
        attrs = {"id": sid, "dir": "ltr", "class": "source-table", "data-source-summary": summary,
                 "aria-label": translation["table_summary_overrides"].get(sid, summary),
                 "data-source-tgroup-cols": group.get("cols")}
        if override:
            attrs.update({"aria-describedby": "toolkit-table-summary", "data-description-origin": "original-correction"})
        labels = [n for n in original if tag(n) == "label"]
        if labels:
            check("empty_source_label:" + sid, len(labels) == 1 and len(labels[0]) == 0 and not text(labels[0]))
            attrs["data-source-empty-label"] = "true"
        if original.get("class"):
            attrs["data-source-class"] = original.get("class")
        check("table_exact_attributes:" + sid, target.tag == "table" and target.attrib == attrs)
        groups = [n for n in group if tag(n) in ("thead", "tbody")]
        check("table_exact_child_groups:" + sid, [n.tag for n in target] == ["colgroup", *[tag(n) for n in groups]]
              and pure(target))
        colgroup = target[0]
        check("source_colspec_preserved:" + sid, colgroup.attrib == {} and pure(colgroup)
              and len(colgroup) == len(columns) == int(group.get("cols")))
        for i, (left, right) in enumerate(zip(columns, colgroup)):
            check(f"exact_colspec:{sid}:{i}", right.tag == "col" and len(right) == 0 and right.text in (None, "")
                  and right.attrib == {"data-source-" + k: v for k, v in left.attrib.items()})
        wrapper = rp[target]
        check("table_scroll_wrapper:" + sid, wrapper.tag == "div" and wrapper.attrib == {
            "class": "table-scroll source-table-scroll", "dir": "ltr", "tabindex": "0", "role": "region",
            "aria-label": "جدول؛ لوڑ پئے تے پاسے سرکاؤ"} and len(wrapper) == 1 and wrapper[0] is target and pure(wrapper))
        container = rp[wrapper]
        check("table_container_exact:" + sid, container.tag == "div"
              and container.attrib == {"class": "source-table-container", "data-source-child": sid}
              and len(container) == (2 if override else 1) and container[0] is wrapper and pure(container))
        if override:
            advisory = ET.fromstring('<p class="scroll-hint source-summary-advisory">ایس جدول دے ماخذی خلاصے بارے <a href="#toolkit-table-summary">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>')
            check("summary_advisory_exact:" + sid, signature(container[1]) == signature(advisory))
        for left, right in zip(groups, list(target)[1:]):
            check("table_group_rows:" + sid + ":" + tag(left), right.tag == tag(left) and right.attrib == {}
                  and len(left) == len(right) and pure(right))
        source_data, target_data = source_rows(original), reader_rows(target)
        check("physical_rows:" + sid, len(source_data) == len(target_data))
        matrix = []
        colnames = {n.get("colname"): i for i, n in enumerate(columns)}
        for ri, (left, right) in enumerate(zip(source_data, target_data), 1):
            row_attrs = {"data-source-" + k: v for k, v in left.attrib.items()}
            check(f"row_pure_shape:{sid}:{ri}", right.tag == "tr" and right.attrib == row_attrs
                  and len(left) == len(right) and pure(right))
            occupied, values = 0, []
            for ci, (entry, cell) in enumerate(zip(left, right), 1):
                key = f"{sid}/row/{ri}/entry/{ci}"
                span = 1
                if entry.get("namest"):
                    check("span_start_matches_source:" + key, colnames[entry.get("namest")] == occupied)
                    span = colnames[entry.get("nameend")] - colnames[entry.get("namest")] + 1
                occupied += span
                keyed = key in source_specs(source)
                is_head = tag(op[left]) == "thead" or (sid != TABLES[0] and ci == 1)
                cell_attrs = {"dir": "rtl" if keyed else "ltr"}
                if keyed:
                    cell_attrs["data-source-key"] = key
                if is_head:
                    cell_attrs["scope"] = ("colgroup" if span > 1 else "col") if tag(op[left]) == "thead" else "row"
                if span > 1:
                    cell_attrs["colspan"] = str(span)
                for k, v in entry.attrib.items():
                    cell_attrs["data-source-" + k] = v
                if entry.get("align") == "center":
                    cell_attrs["style"] = "text-align:center"
                if not keyed and not len(entry) and re.search("[A-Za-z]", text(entry)):
                    cell_attrs["lang"] = "en"
                check("cell_semantic_attributes:" + key, cell.tag == ("th" if is_head else "td") and cell.attrib == cell_attrs)
                if not keyed:
                    if len(entry):
                        check("pure_media_cell:" + key, len(entry) == len(cell) == 1 and tag(entry[0]) == "media"
                              and cell[0].tag == "div" and cell[0].attrib == {
                                  "class": "source-media", "data-source-child": entry[0].get("id")} and pure(cell))
                    else:
                        check("untranslated_data_exact:" + key, len(cell) == 0 and cell.text == text(entry))
                values.append(text(cell))
            check(f"source_column_occupancy:{sid}:{ri}", occupied == int(group.get("cols")))
            matrix.append(values)
        report.append({"id": sid, "physical_rows": len(source_data), "columns": len(columns),
                       "cell_counts": [len(row) for row in source_data], "rendered_cells": matrix})
    check("exact_5x2_11x3span_9x2_shapes", [n["cell_counts"] for n in report] == [[2] * 5, [1] + [3] * 10, [2] * 9])
    check("no_equation_table_invented_caption", not by_id(document, TABLES[2]).findall("caption"))
    check("equation_summary_original_dots", by_id(document, TABLES[2]).get("data-source-summary") == ".."
          and by_id(document, TABLES[2]).get("aria-label") != "..")
    check("toolkit_summary_title_count_corrected", "دس قطاراں" in by_id(document, TABLES[1]).get("data-source-summary")
          and "گیاراں" in by_id(document, TABLES[1]).get("aria-label"))
    return report


def source_link_specs(source):
    return [(key, i, link) for key, node in source_specs(source).items() if tag(node) not in ("table", "media")
            for i, link in enumerate(n for n in node if tag(n) == "link")]


def expected_reference(source, target):
    local = any(n.get("id") == target for n in source.iter())
    kind = "example" if target.startswith("Example_") else "table" if target.startswith("Table_") else "figure"
    number = int(target.rsplit("_", 1)[1])
    label = str(number) if kind == "example" else "1.1." + str(number)
    if local:
        unit = "008"
    elif kind == "figure" and target == "Figure_01_01_001":
        unit = "001"
    else:
        require("known_prior_example_reference", kind == "example" and 1 <= number <= 12)
        unit = "002" if number == 1 else "003" if number == 2 else "004" if number <= 4 else "005" if number == 5 else "006" if number <= 8 else "007"
    return {"id": target, "kind": kind, "local_label": label, "unit": "PNB-" + unit,
            "href": ("#" if local else "unit-" + unit + ".html#") + target}


def validate_links(document, source, translation, manifest, check=require):
    specs = source_link_specs(source)
    ids = list(dict.fromkeys(link.get("target-id") for _, _, link in specs if link.get("target-id")))
    expected_refs = [expected_reference(source, sid) for sid in ids]
    check("all_manifest_reference_destinations", manifest["references"] == expected_refs)
    external_keys = [f"{key}/link/{i}" for key, i, link in specs if link.get("url")]
    check("six_exact_external_label_keys", len(external_keys) == 6 and list(translation["source_link_labels"]) == external_keys)
    actual_marked = [n for n in document.iter() if n.get("data-source-link")]
    check("37_marked_source_links_in_order", len(specs) == len(actual_marked) == 37
          and [n.get("data-source-link") for n in actual_marked] == [f"{key}/link/{i}" for key, i, _ in specs])
    report, counts = [], {"local": 0, "cross_unit": 0, "external": 0}
    for (key, index, original), actual in zip(specs, actual_marked):
        marker = f"{key}/link/{index}"
        owner = target_block(document, source, key, source_specs(source)[key])
        check("source_link_direct_owner:" + marker, actual in list(owner))
        if original.get("url"):
            href = original.get("url")
            label = translation["source_link_labels"][marker]
            expected = ET.Element("a", {"data-source-link": marker, "href": href})
            expected.text = label
            counts["external"] += 1
        else:
            spec = expected_reference(source, original.get("target-id"))
            href = spec["href"]
            noun = {"figure": "شکل", "table": "جدول", "example": "مثال"}[spec["kind"]]
            expected = ET.Element("a", {"data-source-link": marker, "href": href})
            expected.text = noun + " "
            ET.SubElement(expected, "bdi", {"dir": "ltr"}).text = spec["local_label"]
            counts["local" if href.startswith("#") else "cross_unit"] += 1
        check("exact_source_link:" + marker, signature(actual) == signature(expected))
        report.append({"key": marker, "href": href, "label": text(actual)})
    check("17local14cross6external", counts == {"local": 17, "cross_unit": 14, "external": 6})
    local_files = []
    for node in document.iter():
        for name in ("href", "src"):
            if not node.get(name):
                continue
            raw = node.get(name)
            parsed = urlsplit(raw)
            if parsed.scheme in ("http", "https", "mailto"):
                continue
            check("local_url_scheme:" + raw, not parsed.scheme and not parsed.netloc)
            resolved = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            check("local_target_exists:" + raw, resolved.is_file() and resolved.is_relative_to(BASE.resolve()))
            if parsed.fragment:
                target_doc = document if resolved == READER.resolve() else parse_reader(resolved.read_text(encoding="utf-8"))
                check("local_anchor_exists:" + raw, len([n for n in target_doc.iter() if n.get("id") == unquote(parsed.fragment)]) == 1)
            local_files.append(raw)
    return {"source_links": report, "counts": counts, "local_destinations": local_files}


def validate_images(document, source, translation, manifest, notices, check=require):
    media = [n for n in source.iter() if tag(n) == "media"]
    check("15_images_and_notices", len(media) == len(manifest["images"]) == len(notices) == 15
          and len(list(document.iter("img"))) == 15)
    op, rp = parents(source), parents(document)
    with (ROOT / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv").open(encoding="utf-8-sig", newline="") as stream:
        rights = list(csv.DictReader(stream))
    notes, report = {}, []
    for original, spec, notice in zip(media, manifest["images"], notices):
        sid = original.get("id")
        check("manifest_actual_media_ID:" + sid, spec["media_id"] == sid and len(original) == 1
              and original[0].get("src") == "../../" + spec["source_path"])
        is_figure = tag(op[original]) == "figure"
        check("real_or_absent_figure_ID:" + sid, (spec.get("figure_id") == op[original].get("id")) if is_figure
              else "figure_id" not in spec and "local_label" not in spec and tag(op[original]) == "entry")
        note = ("toolkit-alt-three-panels" if sid == "fs-id1165137786563" else "toolkit-alt-graphs") if is_figure else "toolkit-alt-values"
        notes[sid] = note
        actual = by_id(document, sid)
        asset = BASE / spec["path"]
        canonical = ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle" / spec["source_path"]
        check("source_asset_hash_and_copy:" + sid, sha256(asset) == sha256(canonical) == spec["sha256"] == notice["sha256"])
        matches = [row for row in rights if row["asset_path"] == spec["source_path"]]
        check("exact_existing_whole_notice:" + sid, len(matches) == 1 and matches[0] == notice
              and notice["source_modules"] == "m49301" and notice["admission"] == "admitted")
        dimensions = jpeg_dimensions(asset.read_bytes())
        check("actual_image_dimensions:" + sid, dimensions == (spec["width"], spec["height"])
              and len(asset.read_bytes()) == int(notice["bytes"]))
        expected_attrs = {"id": sid, "src": "../" + spec["path"], "width": str(dimensions[0]), "height": str(dimensions[1]),
                          "style": f"--source-width:{dimensions[0]}px", "alt": translation["image_alt_overrides"][sid],
                          "data-source-alt": translation["source_blocks"][sid + "/alt"], "aria-describedby": note,
                          "data-description-origin": "original-accessibility-addition"}
        check("image_exact_attributes:" + sid, actual.tag == "img" and actual.attrib == expected_attrs
              and len(actual) == 0 and actual.text in (None, ""))
        wrapper = rp[actual]
        check("image_focus_wrapper:" + sid, wrapper.tag == "div" and wrapper.attrib == {
            "class": "figure-scroll", "dir": "ltr", "tabindex": "0", "role": "region", "aria-label": "اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ"}
            and len(wrapper) == 1 and wrapper[0] is actual and pure(wrapper))
        container = rp[wrapper]
        check("media_container_pure:" + sid, container.tag == "div"
              and container.attrib == {"class": "source-media", "data-source-child": sid}
              and len(container) == 3 and container[0] is wrapper and pure(container))
        hint = ET.fromstring(f'<p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="../{spec["path"]}">اصل شکل وکھری کھولو</a>۔</p>')
        advisory = ET.fromstring(f'<p class="scroll-hint source-alt-advisory">ایس شکل دے ماخذ والے متبادل متن بارے <a href="#{note}">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>')
        check("image_hint_and_advisory_exact:" + sid, signature(container[1]) == signature(hint)
              and signature(container[2]) == signature(advisory))
        check("image_note_in_original_bridge:" + sid, by_id(document, note) in list(by_id(document, "toolkit-bridge").iter()))
        report.append({"media_id": sid, "figure_id": spec.get("figure_id"), "asset": spec["path"],
                       "sha256": spec["sha256"], "dimensions": dimensions, "notice": notice["rights_component_id"], "note": note})
    check("all15_override_note_mappings", translation["image_alt_note_ids"] == notes
          and set(translation["image_alt_overrides"]) == set(notes))
    check("six_genuine_figures_nine_table_media", sum(n["figure_id"] is not None for n in report) == 6)
    return report


def right_hand_side(math_node):
    row = math_node.find("{" + MATH + "}mrow")
    require("toolkit_equation_mrow", row is not None)
    equal = [i for i, n in enumerate(row) if tag(n) == "mo" and n.text == "="]
    require("toolkit_single_equality", len(equal) == 1)
    lhs = "".join(text(n) for n in list(row)[:equal[0]])
    require("toolkit_f_x_input", compact(lhs) == "f(x)")
    result = ET.Element("{" + MATH + "}mrow")
    for node in list(row)[equal[0] + 1:]:
        if tag(node) == "mo" and (node.text or "") in ("", ",", "."):
            continue
        result.append(copy.deepcopy(node))
    return result


def formula_shape(node):
    name = tag(node)
    if name in ("mi", "mn", "mo"):
        return (node.text or "").strip()
    if name in ("math", "mrow"):
        return "".join(formula_shape(n) for n in node)
    if name == "mfrac":
        return "(" + formula_shape(node[0]) + ")/(" + formula_shape(node[1]) + ")"
    if name == "msup":
        return "(" + formula_shape(node[0]) + ")^(" + formula_shape(node[1]) + ")"
    if name == "msqrt":
        return "sqrt(" + "".join(formula_shape(n) for n in node) + ")"
    if name == "mroot":
        return "root(" + formula_shape(node[1]) + "," + formula_shape(node[0]) + ")"
    raise AssertionError("unsupported_toolkit_formula_node:" + name)


def evaluate_rule(node, x, c=2):
    name = tag(node)
    if name == "mi":
        require("only_source_toolkit_variables", node.text in ("x", "c"))
        return x if node.text == "x" else c
    if name == "mn":
        return float(node.text)
    if name in ("math", "mrow"):
        children = list(node)
        if len(children) == 3 and children[0].text == children[2].text == "|":
            return abs(evaluate_rule(children[1], x, c))
        require("single_toolkit_rhs_component", len(children) == 1)
        return evaluate_rule(children[0], x, c)
    if name == "mfrac":
        return evaluate_rule(node[0], x, c) / evaluate_rule(node[1], x, c)
    if name == "msup":
        return evaluate_rule(node[0], x, c) ** evaluate_rule(node[1], x, c)
    if name == "msqrt":
        require("single_square_root_radicand", len(node) == 1)
        return math.sqrt(evaluate_rule(node[0], x, c))
    if name == "mroot":
        require("real_cube_root_degree", evaluate_rule(node[1], x, c) == 3)
        value = evaluate_rule(node[0], x, c)
        return math.copysign(abs(value) ** (1 / 3), value)
    raise AssertionError("unsupported_toolkit_arithmetic:" + name)


def pairs_from_text(value):
    return [(float(x), float(y)) for x, y in re.findall(
        r"\(([-0-9.]+),([-0-9.]+)\)", value.replace("−", "-").replace(" ", ""))]


def validate_arithmetic(document, source, check=require):
    grades = [[text(cell) for cell in row] for row in source_rows(by_id(source, TABLES[0]))[1:]]
    displayed = [[text(cell) for cell in row] for row in reader_rows(by_id(document, TABLES[0]))[1:]]
    check("exact_four_grade_pairs", displayed == grades == [["A", "4.0"], ["B", "3.0"], ["C", "2.0"], ["D", "1.0"]])
    check("given_grade_mapping_and_reverse_unique", len({x for x, _ in grades}) == len({y for _, y in grades}) == 4)
    pixel_table = by_id(document, "toolkit-pixel-values")
    rows = pixel_table.findall("tbody/tr")
    check("nine_readable_pixel_rows", len(rows) == 9 and all(len(row) == 2 for row in rows))
    observed = [pairs_from_text(text(row[1])) for row in rows]
    check("all39_inspected_pixel_pairs_exact", observed == PIXEL_PAIRS and sum(map(len, observed)) == 39)
    families = ["c", "x", "|x|", "(x)^(2)", "(x)^(3)", "(1)/(x)", "(1)/((x)^(2))", "sqrt(x)", "root(3,x)"]
    rule_sets = []
    for sid, offset in ((TABLES[1], 2), (TABLES[2], 0)):
        originals = source_rows(by_id(source, sid))[offset:]
        rendered = reader_rows(by_id(document, sid))[offset:]
        check("nine_rule_rows:" + sid, len(originals) == len(rendered) == 9)
        rules = []
        for index, (original, actual, samples) in enumerate(zip(originals, rendered, observed)):
            source_rule = right_hand_side(next(original[1].iter("{" + MATH + "}math")))
            target_rule = right_hand_side(next(actual[1].iter("{" + MATH + "}math")))
            check(f"source_rule_family:{sid}:{index}", formula_shape(source_rule) == formula_shape(target_rule) == families[index])
            for x, y in samples:
                check(f"displayed_formula_sample:{sid}:{index}:{x}", math.isclose(evaluate_rule(target_rule, x), y, rel_tol=1e-12, abs_tol=1e-12)
                      and math.isclose(evaluate_rule(source_rule, x), y, rel_tol=1e-12, abs_tol=1e-12))
            rules.append(target_rule)
        rule_sets.append(rules)
        for index in (5, 6):
            rejected = False
            try:
                evaluate_rule(rules[index], 0)
            except ZeroDivisionError:
                rejected = True
            check(f"zero_excluded_denominator:{sid}:{index}", rejected)
        rejected = False
        try:
            evaluate_rule(rules[7], -1)
        except ValueError:
            rejected = True
        check("negative_excluded_real_square_root:" + sid, rejected)
        check("principal_square_root_nonnegative:" + sid, evaluate_rule(rules[7], 4) == 2)
        check("negative_real_cube_root:" + sid, math.isclose(evaluate_rule(rules[8], -8), -2))
        check("constant_c_not_fixed_to_image2:" + sid, all(evaluate_rule(rules[0], x, c=-7) == -7 for x in (-2, 0, 2)))
        check("identity_preserves_input:" + sid, all(evaluate_rule(rules[1], x) == x for x in (-2, 0, 2)))
        check("noninjective_absolute_and_square:" + sid, evaluate_rule(rules[2], -2) == evaluate_rule(rules[2], 2) == 2
              and evaluate_rule(rules[3], -2) == evaluate_rule(rules[3], 2) == 4)
    table_media = [n for n in by_id(source, TABLES[1]).iter() if tag(n) == "media"]
    for i, node in enumerate(table_media):
        pairs = pairs_from_text(by_id(document, node.get("id")).get("alt"))
        check("image_alt_sample_pairs:" + node.get("id"), pairs[-len(PIXEL_PAIRS[i]):] == PIXEL_PAIRS[i])
    # These are the actual supplied answer lists, not invented reverse assignments.
    for sid, english, punjabi in (("eip-idm552643792", ["yes", "no", "no"], ["ہاں", "نہیں", "نہیں"]),
                                ("fs-id1165137655291", ["Yes", "No"], ["ہاں", "نہیں"])):
        original, target = by_id(source, sid), by_id(document, sid)
        for i, (left, right) in enumerate(zip(original, target)):
            source_answer = re.sub(r"^[ⓐⓑⓒ]\s*", "", text(left))
            displayed_answer = re.sub(r"^\([abc]\)\s*", "", text(right))
            check(f"supplied_answer_polarity:{sid}:{i}", source_answer.startswith(english[i]) and displayed_answer.startswith(punjabi[i]))
    for sid, expected_source, expected_target in (("fs-id1165134258609", "yes", "ہاں۔"),
                                                ("fs-id1165135255385", "No, because it does not pass the horizontal line test.", "نہیں، کیوں جے ایہہ لیٹی لکیر دی پرکھ وچ پورا نہیں اُتردا۔")):
        check("graph_supplied_answer:" + sid, text(by_id(source, sid)) == expected_source and text(by_id(document, sid)) == expected_target)
    # The selected English uses exactly these geometric formula tokens.
    radius_source = list(by_id(source, "fs-id1165134148470").iter("{" + MATH + "}math"))[1]
    radius_display = list(by_id(document, "fs-id1165134148470").iter("{" + MATH + "}math"))[1]
    check("area_radius_formula_tokens", compact(text(radius_source)) == "A=πr2," and compact(text(radius_display)) == "A=πr2")
    inverse = list(by_id(document, "fs-id1165137892326").iter("{" + MATH + "}math"))[2]
    check("positive_radius_inverse_root_structure", formula_shape(inverse) == "sqrt((A)/(π))")
    for radius in (0.25, 0.5, 1, 2, 5):
        area = math.pi * radius ** 2
        check("radius_area_roundtrip:" + str(radius), math.isclose(math.sqrt(area / math.pi), radius))
    graph_maths = list(by_id(document, "fs-id1165137637786").iter("{" + MATH + "}math"))
    check("source_graph_two_inputs_outputs", [compact(text(graph_maths[i])) for i in (8, 9, 12, 13)]
          == ["f(0)=2", "f(6)=1", "(0,2)", "(6,1)"])
    check("source_grade100_not_silently101", re.findall(r"\d+", text(by_id(document, "fs-id1165137655291")[1])) == ["100"])
    return {"grade_pairs": grades, "image_table_pairs": observed, "formula_families": families,
            "formula_sample_comparisons": 78, "claim_limit": "Finite samples check source consistency, not universal graph behavior or grading policy. Positive-radius uniqueness follows from monotonic squaring on that domain; graphs are also independently inspected pinned images."}


def validate_bridge(document, source, translation, check=require):
    main = document.find("body/main")
    for key in ("bridge_before_html", "bridge_after_html"):
        expected = ET.fromstring(translation[key])
        actual = by_id(document, expected.get("id"))
        check("original_separate_from_source:" + key, actual in list(main) and actual.get("class") == "original")
        check("original_fragment_exact:" + key, signature(actual) == signature(expected))
    original_ids = {n.get("id") for n in by_id(document, "toolkit-bridge").iter() if n.get("id")}
    check("original_ids_not_source_ids", not original_ids.intersection(n.get("id") for n in source.iter() if n.get("id")))
    bdis = lambda sid: [compact(text(n)) for n in by_id(document, sid).iter("bdi")]
    check("corrected_old_figure_arrows", bdis("toolkit-injective-precision") == ["(b)", "p→x,q→y,r→z", "(a)", "q→n", "r→n"])
    check("percent_count_explicit_domains", bdis("toolkit-grade-count") == ["100", "0", "100", "101", "1", "100", "100"]
          and len(range(101)) == 101 and len(range(1, 101)) == 100)
    check("radius_precision_bdis", bdis("toolkit-circle-domain") == ["r>0", "A>0", "A=πr²", "r=√(A/π)"])
    check("circle_intersections_and_retained_axis", bdis("toolkit-test-precision") == [
        "3", "−3<x<3", "x=−3", "x=3", "x=2", "y=√5", "y=−√5", "f(x)", "y"])
    check("circle_counterexample_arithmetic", math.isclose(2 ** 2 + math.sqrt(5) ** 2, 3 ** 2)
          and math.sqrt(5) != -math.sqrt(5))
    check("function_prerequisite_before_horizontal", "فنکشن ہی نہیں" in text(by_id(document, "toolkit-test-precision")))
    check("curve_and_equation_limits_disclosed", "لازماً ہموار وکر نہیں" in text(by_id(document, "toolkit-generalization"))
          and "ہر مساوات لئی نہیں" in text(by_id(document, "toolkit-generalization")))
    check("summary_source_dots_disclosed", bdis("toolkit-table-summary") == [".."])
    check("three_panel_correction_labels", bdis("toolkit-alt-three-panels") == ["(c)", "(a)", "(b)", "(c)"])
    check("graph_legend_values", bdis("toolkit-alt-graphs") == ["Function", "NotaFunction", "f(0)=2", "f(6)=1", "y=3"])
    check("domain_conditions_original_only", bdis("toolkit-domains") == ["1/x", "1/x²", "x≠0", "x≥0", "√x≥0", "1/x", "(−2)²=2²=4", "|−2|=|2|=2"])
    check("nine_pixel_row_labels", len(by_id(document, "toolkit-pixel-values").findall("tbody/tr")) == 9)
    check("twelve_provisional_terms", len(by_id(document, "toolkit-term-key").findall("tbody/tr")) == 12)
    check("human_review_not_claimed", "پنجابی استاد دی تصدیق نہیں" in text(by_id(document, "toolkit-bridge")))
    return {"original_note_ids": sorted(original_ids), "source_corrections_separate": True}


def validate_directions(document, source, check=require):
    p = parents(document)

    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = p.get(node)
        return None

    check("every_bdi_LTR", all(n.get("dir") == "ltr" for n in document.iter("bdi")))
    check("every_English_lane_LTR", all(direction(n) == "ltr" for n in document.iter() if n.get("lang") == "en"))
    for node in document.find("body").iter():
        for index, value in enumerate([node.text or "", *[n.tail or "" for n in node]]):
            if re.search("[A-Za-z0-9]", value):
                check(f"visible_Latin_digits_LTR:{node.tag}:{node.get('id')}:{index}", direction(node) == "ltr")
    for key, original in source_specs(source).items():
        if tag(original) not in ("table", "media"):
            check("source_prose_RTL:" + key, direction(target_block(document, source, key, original)) == "rtl")


UNIT_CSS = '''
.source-media { max-width:100%; }
.source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; }
.source-table td[dir="rtl"] { white-space:normal; font-family:inherit; }
#Table_01_01_14 { width:890px; min-width:890px; table-layout:fixed; }
#Table_01_01_14 col:nth-child(1) { width:170px; }
#Table_01_01_14 col:nth-child(2) { width:170px; }
#Table_01_01_14 col:nth-child(3) { width:550px; }
#Table_01_01_14 th[colspan] { text-align:left; }
#Table_01_01_14 .source-media { width:100%; }
#Table_01_01_14 .scroll-hint { white-space:normal; font-family:inherit; direction:rtl; }
#toolkit-pixel-values td { white-space:nowrap; }
.source-summary-advisory { direction:rtl; }
'''


def validate_metadata(document, translation, manifest, check=require):
    check("reader_locale_attributes", document.attrib == {"lang": "pnb-Arab-PK", "dir": "rtl"}
          and translation["locale"] == "pnb-Arab-PK" and translation["unit"] == manifest["unit"] == "PNB-008")
    check("document_structure", [n.tag for n in document] == ["head", "body"]
          and [n.tag for n in document.find("body")] == ["header", "main", "footer"])
    check("page_containers_attributes", all(document.find(path).attrib == {} for path in ("head", "body", "body/header", "body/main")))
    check("page_no_extra_own_text", not (document.text or "").strip() and not (document.find("body").text or "").strip()
          and all(not (n.tail or "").strip() for n in document.find("body"))
          and all(not (n.tail or "").strip() for n in document))
    head = document.find("head")
    check("head_no_script_or_extra_nodes", [n.tag for n in head] == ["meta", "meta", "meta", "title", "style"])
    check("metadata_exact", [n.attrib for n in head[:3]] == [
        {"charset": "utf-8"}, {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Shahmukhi Punjabi algebra-to-functions bridge; incremental translation unit"}])
    check("metadata_leaf_and_tail_purity", not (head.text or "").strip()
          and all(not (n.tail or "").strip() for n in head)
          and all(len(n) == 0 and not (n.text or "").strip() for n in head[:3]))
    check("unit_title_exact", text(head.find("title")) == translation["title"] + " — PNB-008"
          and head.find("title").attrib == {} and len(head.find("title")) == 0)
    check("source_CSS_and_scoped_addition_exact", head.find("style").text == (BASE / "styles/reader.css").read_text(encoding="utf-8") + UNIT_CSS
          and head.find("style").attrib == {} and len(head.find("style")) == 0)
    header = document.find("body/header")
    check("header_child_order", [n.tag for n in header] == ["p", "h1", "p", "p", "nav"])
    check("header_no_injected_text_or_tails", not (header.text or "").strip()
          and all(not (n.tail or "").strip() for n in header))
    check("header_title_subtitle", text(header[1]) == translation["title"] and text(header[2]) == translation["subtitle"]
          and header[1].attrib == header[2].attrib == {} and len(header[1]) == len(header[2]) == 0)
    check("unit_eyebrow", header[0].attrib == {"class": "eyebrow"} and len(header[0]) == 1
          and header[0][0].attrib == {"dir": "ltr"} and text(header[0]) == "PNB-008 · A30 / m49301")
    eyebrow = ET.fromstring('<p class="eyebrow"><bdi dir="ltr">PNB-008 · A30 / m49301</bdi></p>')
    check("unit_eyebrow_exact", signature(header[0]) == signature(eyebrow))
    check("review_status_exact", header[3].attrib == {"class": "status"} and len(header[3]) == 0
          and text(header[3]) == "ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی")
    check("previous_source_terminology_navigation", [n.get("href") for n in header[4]] == ["unit-007.html", "#" + SELECTED[0], "#terminology"])
    navigation = ET.fromstring('<nav aria-label="سبق دے حصے"><a href="unit-007.html">پچھلا سبق</a> · <a href="#' + SELECTED[0] + '">ماخذ دا ترجمہ</a> · <a href="#terminology">اصطلاحاں</a></nav>')
    check("navigation_exact_text_and_tails", signature(header[4]) == signature(navigation))
    footer = by_id(document, "credits")
    check("footer_topology_and_direction", footer.attrib == {"id": "credits", "lang": "en", "dir": "ltr"}
          and [n.tag for n in footer] == ["h2", "p", "p", "p"]
          and all(n.attrib == {} for n in footer) and not (footer.text or "").strip()
          and all(not (n.tail or "").strip() for n in footer))
    check("credit_identity_and_scope", all(part in text(footer) for part in ("Jay Abramson", "David Lippman", "Melonie Rasmussen",
          "Rice University", "OpenStax", "CC BY-NC-SA 4.0", "do not endorse", "Six genuine source figures", "nine unnumbered toolkit media",
          "unit-008-component-notices.json", "All 49 source MathML trees", "one owner-bound numeric 1.", "one question-mark token",
          "No native-speaker approval is claimed", "not a complete textbook")))
    expected_urls = ["https://github.com/openstax/osbooks-college-algebra-bundle/blob/" + manifest["commit"] + "/" + manifest["path"],
                     "../provenance/ATTRIBUTION.md", "https://creativecommons.org/licenses/by-nc-sa/4.0/"]
    check("credit_source_and_license_links", [n.get("href") for n in footer.iter("a")] == expected_urls)
    # Fixed, reviewed documentary notices are checked exactly, not merely by
    # required substrings that could coexist with a contradictory added claim.
    credits = [
        '<h2>Sources, credits and changes</h2>',
        '<p>Adapted from <a href="' + expected_urls[0] + '">OpenStax Precalculus 2e, module m49301</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Figure copyright Rice University, OpenStax, under CC BY-NC-SA 4.0. Full contributor notices remain in <a href="../provenance/ATTRIBUTION.md">the provenance record</a>. Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to retained component notices. OpenStax and Rice University do not endorse this adaptation; no cover or trademarks are reproduced. Six genuine source figures use local reader labels; nine unnumbered toolkit media stay within their table cells. All fifteen original JPEGs are unchanged. Faithful source alts remain in data-source-alt; original expanded accessible descriptions link to visible notes. Exact existing component records are retained in unit-008-component-notices.json. The toolkit title spans its three original columns, and the equation table remains unnumbered. Earlier-unit references preserve their destination IDs; six historical external URLs are retained without a current-availability claim.</p>',
        '<p>Changes: Shahmukhi Punjabi translation of the declared source selection, with original explanatory additions labeled separately. Source identifiers, table data, proper names and mathematical content are retained. Where present, source circled-letter parts are displayed as isolated Latin-letter labels with the same correspondence. Unit-specific source ambiguities and accessibility-summary corrections are disclosed in the original bridge notes and provenance record. No native-speaker approval is claimed. All 49 source MathML trees retain their node order. Standalone terminal periods/commas and exactly one owner-bound numeric 1. and one question-mark token are relocated into Punjabi prose by reversible data-source-text-edits; internal mathematical punctuation, roots, fractions and scripts remain. Source emphasis without an explicit effect is displayed as strong, not silently italicized. The frozen source is unchanged.</p>',
        '<p>Indonesian comparison edition: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1. Its stated process provenance is OpenAI Codex gpt-5.6-sol, Ultra. This pilot was produced with OpenAI Codex assistance at the user\'s direction; source and human-contributor credits are not replaced. This is a local translation pilot, not a complete textbook or a model-training corpus.</p>',
    ]
    check("credit_notices_exact", all(signature(n) == signature(ET.fromstring(expected)) for n, expected in zip(footer, credits)))
    with (BASE / "terminology.tsv").open(encoding="utf-8", newline="") as stream:
        terms = list(csv.DictReader(stream, delimiter="\t"))
    ledger = by_id(document, "terminology")
    rows = ledger.findall("./div/table/tbody/tr")
    check("shared_terminology_rows", [[text(n) for n in row] for row in rows]
          == [[term["pnb-Arab-PK"], term["ur-Arab-PK"], term["en"]] for term in terms])
    expected_ledger = '<section id="terminology"><h2>تِن زباناں دی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
    expected_ledger += ''.join('<tr><td>' + html.escape(row["pnb-Arab-PK"]) + '</td><td lang="ur-Arab-PK">' + html.escape(row["ur-Arab-PK"]) + '</td><td lang="en" dir="ltr">' + html.escape(row["en"]) + '</td></tr>' for row in terms)
    expected_ledger += '</tbody></table></div></section>'
    check("shared_terminology_complete_structure", signature(ledger) == signature(ET.fromstring(expected_ledger)))
    return {"locale": "pnb-Arab-PK", "title": translation["title"], "shared_terms": len(terms)}


def validate_unicode(document, check=require):
    check("reader_unicode_gate", FORBIDDEN.search(ET.tostring(document, encoding="unicode")) is None)


def mutations(document, source, translation, manifest, notices, check):
    tested = []
    contexts = math_contexts(document, source)
    maths = lambda root: list(root.iter("{" + MATH + "}math"))
    mv = lambda root: validate_math(root, source)
    sv = lambda root: validate_structure(root, source)
    bv = lambda root: validate_blocks(root, source, translation)
    tv = lambda root: validate_tables(root, source, translation)
    lv = lambda root: validate_links(root, source, translation, manifest)
    iv = lambda root: validate_images(root, source, translation, manifest, notices)
    av = lambda root: validate_arithmetic(root, source)
    ov = lambda root: validate_bridge(root, source, translation)
    dv = lambda root: validate_directions(root, source)
    meta = lambda root: validate_metadata(root, translation, manifest)

    def reject(name, change, validator, prefix):
        detached = copy.deepcopy(document)
        change(detached)
        try:
            validator(detached)
        except AssertionError as error:
            check("mutation_rejected:" + name, str(error).startswith(prefix))
            tested.append({"mutation": name, "rejection": str(error)})
        else:
            raise AssertionError("mutation_not_rejected:" + name)

    reject("changed_area_exponent", lambda d: next(d.iter("{" + MATH + "}mn")).__setattr__("text", "3"), mv, "exact_math_reconstruction")

    def ledger_value(d, field, value, context=("fs-id1165137637786", 9)):
        node = maths(d)[contexts.index(context)]
        entries = json.loads(node.get(LEDGER))
        entries[0][field] = value
        if field == "new":
            at_path(node, entries[0]["path"]).text = value
        node.set(LEDGER, json.dumps(entries))

    reject("forged_numeric_ledger_old", lambda d: ledger_value(d, "old", "8."), mv, "ledger_old_matches_source")
    reject("reversible_numeric_semantic_change", lambda d: ledger_value(d, "new", "8"), mv, "ledger_new_matches_policy")
    reject("question_mark_changed_to_operator", lambda d: ledger_value(d, "new", "+", ("fs-id1165137761111", 0)), mv, "ledger_new_matches_policy")

    def forge_internal_comma(d):
        originals = list(source.iter("{" + MATH + "}math"))
        index, path = next((i, path) for i, original in enumerate(originals) for path, leaf in paths(original)
                           if tag(leaf) == "mo" and leaf.text == "," and path not in permitted_edits(original, contexts[i]))
        node = maths(d)[index]
        at_path(node, path).text = ""
        entries = json.loads(node.get(LEDGER, "[]"))
        entries.append({"path": list(path), "old": ",", "new": ""})
        node.set(LEDGER, json.dumps(entries))

    reject("reversible_internal_pair_comma", forge_internal_comma, mv, "source_position_whitelist")

    def duplicate_path(d):
        node = next(n for n in maths(d) if n.get(LEDGER))
        entries = json.loads(node.get(LEDGER))
        entries.append(copy.deepcopy(entries[0]))
        node.set(LEDGER, json.dumps(entries))

    reject("duplicate_ledger_path", duplicate_path, mv, "ledger_unique_path")
    reject("missing_required_ledger", lambda d: next(n for n in maths(d) if n.get(LEDGER)).attrib.pop(LEDGER), mv, "complete_required_ledger")

    def duplicate_json_key(d):
        node = next(n for n in maths(d) if n.get(LEDGER))
        node.set(LEDGER, node.get(LEDGER).replace('"old":', '"old":"forged","old":', 1))

    reject("duplicate_ledger_JSON_key", duplicate_json_key, mv, "ledger_json_keys_unique")
    reject("math_wrapper_extra_text", lambda d: parents(d)[maths(d)[0]].__setattr__("text", "f(2)=999"), mv, "math_wrapper_pure")
    reject("math_tree_tail_injection", lambda d: maths(d)[0].__setattr__("tail", "x != 0"), mv, "math_wrapper_pure")
    reject("math_hidden_wrapper", lambda d: parents(d)[maths(d)[0]].set("hidden", "hidden"), mv, "math_wrapper_attributes")
    reject("cube_root_degree_changed", lambda d: next(d.iter("{" + MATH + "}mroot"))[1].__setattr__("text", "2"), mv, "exact_math_reconstruction")
    reject("reciprocal_formula_replaced", lambda d: next(by_id(d, TABLES[1]).iter("{" + MATH + "}mfrac"))[0].__setattr__("text", "2"), av, "source_rule_family")
    reject("unkeyed_source_paragraph", lambda d: ET.SubElement(by_id(d, SELECTED[0]), "p", {"dir": "ltr"}).__setattr__("text", "f(2)=999; x != 0"), sv, "complete_structural_children")
    reject("source_container_own_text", lambda d: by_id(d, SELECTED[0]).__setattr__("text", "f(2)=999"), sv, "no_structural_text_or_tails")
    reject("source_child_tail_injection", lambda d: by_id(d, SELECTED[0])[0].__setattr__("tail", "x != 0"), sv, "no_structural_text_or_tails")
    reject("unkeyed_main_paragraph", lambda d: ET.SubElement(d.find("body/main"), "p").__setattr__("text", "f(2)=999"), sv, "complete_main_topology")
    reject("main_tail_injection", lambda d: d.find("body/main")[1].__setattr__("tail", "f(2)=999"), sv, "main_text_tails")
    reject("source_keyed_extra_condition", lambda d: ET.SubElement(by_id(d, "fs-id1165137892387"), "bdi", {"dir": "ltr"}).__setattr__("text", "r != 0"), bv, "exact_block_fragment")
    reject("source_link_tail_injection", lambda d: by_id(d, "fs-id1165135245630").find("a").__setattr__("tail", " f(2)=999"), bv, "exact_block_fragment")
    reject("part_label_changed", lambda d: by_id(d, "eip-id1166399990268").find("span").__setattr__("text", "(b)"), bv, "exact_block_fragment")

    def move_newline(d):
        node = by_id(d, "eip-id1166399990268")
        newline = node.find("br")
        node.remove(newline)
        node.append(newline)

    reject("source_newline_reordered", move_newline, bv, "exact_block_fragment")
    altered_translation = copy.deepcopy(translation)
    emphasis_key = "fs-id1165137628999"
    altered_translation["source_blocks"][emphasis_key] = altered_translation["source_blocks"][emphasis_key].replace("<strong>", "<em>", 1).replace("</strong>", "</em>", 1)
    reject("source_emphasis_even_if_draft_matches", lambda d: by_id(d, emphasis_key).find("strong").__setattr__("tag", "em"),
           lambda d: validate_blocks(d, source, altered_translation), "source_emphasis_style")
    reject("grade_GPA_cell_changed", lambda d: by_id(d, TABLES[0]).find("tbody/tr")[1].__setattr__("text", "4.1"), tv, "untranslated_data_exact")
    reject("grade_letter_data_changed", lambda d: by_id(d, TABLES[0]).find("tbody/tr")[0].__setattr__("text", "E"), av, "exact_four_grade_pairs")

    def swap_rows(d):
        body = by_id(d, TABLES[0]).find("tbody")
        first = body[0]
        body.remove(first)
        body.insert(1, first)

    reject("grade_table_rows_swapped", swap_rows, tv, "untranslated_data_exact")
    reject("toolkit_title_span_changed", lambda d: by_id(d, TABLES[1]).find("thead/tr/th").set("colspan", "2"), tv, "cell_semantic_attributes")
    reject("column_metadata_reordered", lambda d: by_id(d, TABLES[1]).find("colgroup")[0].set("data-source-colname", "c3"), tv, "exact_colspec")
    reject("row_header_demoted", lambda d: by_id(d, TABLES[1]).find("tbody/tr")[0].__setattr__("tag", "td"), tv, "cell_semantic_attributes")
    reject("formula_data_promoted_to_header", lambda d: by_id(d, TABLES[1]).find("tbody/tr")[1].__setattr__("tag", "th"), tv, "cell_semantic_attributes")
    reject("media_cell_extra_paragraph", lambda d: ET.SubElement(by_id(d, TABLES[1]).find("tbody/tr")[2], "p").__setattr__("text", "999"), tv, "pure_media_cell")
    reject("table_transpose_header_orientation", lambda d: by_id(d, TABLES[1]).find("thead").__setattr__("tag", "tbody"), tv, "table_exact_child_groups")
    reject("invented_equation_table_caption", lambda d: ET.SubElement(by_id(d, TABLES[2]), "caption").__setattr__("text", "15"), tv, "table_exact_child_groups")
    reject("source_summary_used_as_ARIA", lambda d: by_id(d, TABLES[1]).set("aria-label", translation["source_blocks"][TABLES[1] + "/summary"]), tv, "table_exact_attributes")
    reject("summary_original_origin_erased", lambda d: by_id(d, TABLES[1]).attrib.pop("data-description-origin"), tv, "table_exact_attributes")
    reject("table_wrapper_hidden", lambda d: parents(d)[by_id(d, TABLES[0])].set("hidden", "hidden"), tv, "table_scroll_wrapper")
    reject("table_container_tail_injection", lambda d: parents(d)[by_id(d, TABLES[1])].__setattr__("tail", "999"), tv, "table_container_exact")

    def summary_link_tail(d):
        table_container = parents(d)[parents(d)[by_id(d, TABLES[1])]]
        table_container[1][0].tail = " CONTRADICTORY f(2)=999"

    reject("summary_advisory_link_tail", summary_link_tail, tv, "summary_advisory_exact")
    first_media = manifest["images"][0]["media_id"]
    reject("wrong_existing_image", lambda d: by_id(d, first_media).set("src", "../" + manifest["images"][1]["path"]), iv, "image_exact_attributes")
    reject("wrong_image_dimension", lambda d: by_id(d, first_media).set("width", "732"), iv, "image_exact_attributes")
    reject("source_alt_silently_replaced", lambda d: by_id(d, "fs-id1165137786563").set("data-source-alt", translation["image_alt_overrides"]["fs-id1165137786563"]), iv, "image_exact_attributes")
    reject("image_original_description_mislabelled", lambda d: by_id(d, first_media).set("data-description-origin", "source"), iv, "image_exact_attributes")
    reject("wrong_existing_alt_note", lambda d: by_id(d, first_media).set("aria-describedby", "toolkit-grade-count"), iv, "image_exact_attributes")
    reject("hidden_image", lambda d: by_id(d, first_media).set("style", "display:none"), iv, "image_exact_attributes")
    reject("media_container_extra_text", lambda d: parents(d)[parents(d)[by_id(d, first_media)]].__setattr__("text", "999"), iv, "media_container_pure")

    def image_link_tail(d):
        container = parents(d)[parents(d)[by_id(d, first_media)]]
        container[-1][0].tail = " EXTRA f(2)=999"

    reject("image_advisory_link_tail", image_link_tail, iv, "image_hint_and_advisory_exact")
    altered_notices = copy.deepcopy(notices)
    altered_notices[0]["attribution"] = "Someone else"
    reject("notice_attribution_changed", lambda d: None, lambda d: validate_images(d, source, translation, manifest, altered_notices), "exact_existing_whole_notice")
    altered_manifest = copy.deepcopy(manifest)
    altered_manifest["images"][6]["figure_id"] = "invented"
    reject("invented_table_media_figure_ID", lambda d: None, lambda d: validate_images(d, source, translation, altered_manifest, notices), "real_or_absent_figure_ID")

    def external(d):
        return by_id(d, "eip-id1165137846437")[0][0]

    reject("external_URL_changed", lambda d: external(d).set("href", "https://example.com/"), lv, "exact_source_link")
    reject("external_label_changed", lambda d: external(d).__setattr__("text", "بدلیا ہویا ناں"), lv, "exact_source_link")
    reject("source_link_marker_changed", lambda d: external(d).set("data-source-link", "wrong/link/0"), lv, "37_marked_source_links_in_order")
    reject("wrong_existing_crossunit_target", lambda d: by_id(d, "fs-id1165137851183")[0][0].set("href", "unit-003.html#Example_01_01_02"), lv, "exact_source_link")
    reject("example_link_mislabelled_figure", lambda d: by_id(d, "fs-id1165137851183")[0][0].__setattr__("text", "شکل "), lv, "exact_source_link")
    reject("bank_answer_reversed", lambda d: by_id(d, "eip-idm552643792")[0][0].__setattr__("tail", " نہیں"), av, "supplied_answer_polarity")
    reject("graph_tryit_answer_reversed", lambda d: by_id(d, "fs-id1165134258609").__setattr__("text", "نہیں۔"), av, "graph_supplied_answer")
    reject("pixel_table_value_changed", lambda d: by_id(d, "toolkit-pixel-values").findall("tbody/tr")[4][1].__setattr__("text", "(−1,−1), (−0.5,−0.5), (0,0), (0.5,0.125), (1,1)"), av, "all39_inspected_pixel_pairs_exact")
    reject("source_100_silently_changed101", lambda d: by_id(d, "fs-id1165137655291")[1].find("bdi").__setattr__("text", "101"), av, "source_grade100_not_silently101")
    reject("original_nonzero_condition_changed", lambda d: next(n for n in by_id(d, "toolkit-domains").iter("bdi") if "≠" in text(n)).__setattr__("text", "x = 0"), ov, "original_fragment_exact")

    def move_original(d):
        node = by_id(d, "toolkit-bridge")
        parents(d)[node].remove(node)
        by_id(d, SELECTED[0]).append(node)

    reject("original_notes_moved_into_source", move_original, ov, "original_separate_from_source")
    reject("body_direction_changed", lambda d: d.find("body").set("dir", "ltr"), dv, "source_prose_RTL")
    reject("numeric_cell_direction_changed", lambda d: by_id(d, TABLES[0]).find("tbody/tr")[1].set("dir", "rtl"), dv, "visible_Latin_digits_LTR")
    reject("unit_metadata_changed", lambda d: d.find("head/title").__setattr__("text", "PNB-009"), meta, "unit_title_exact")
    reject("source_hidden_by_extra_CSS", lambda d: d.find("head/style").__setattr__("text", d.find("head/style").text + "section{display:none}"), meta, "source_CSS_and_scoped_addition_exact")
    reject("source_label_contradictory_tail", lambda d: d.find("body/main")[1][0].__setattr__("tail", " پورا ماخذ مکمل ہو گیا۔"), sv, "source_label_exact")
    reject("metadata_child_injection", lambda d: d.find("head/meta").append(ET.Element("script")), meta, "metadata_leaf_and_tail_purity")
    reject("metadata_title_tail_injection", lambda d: d.find("head/title").__setattr__("tail", " extra title"), meta, "metadata_leaf_and_tail_purity")
    reject("header_own_text_injection", lambda d: d.find("body/header").__setattr__("text", "وکھری دعویٰ"), meta, "header_no_injected_text_or_tails")
    reject("header_child_tail_injection", lambda d: d.find("body/header/h1").__setattr__("tail", "وکھری دعویٰ"), meta, "header_no_injected_text_or_tails")
    reject("eyebrow_hidden", lambda d: d.find("body/header/p/bdi").set("hidden", "hidden"), meta, "unit_eyebrow")
    reject("navigation_link_tail_injection", lambda d: d.find("body/header/nav/a").__setattr__("tail", " پورا ماخذ مکمل ہو گیا۔"), meta, "navigation_exact_text_and_tails")
    reject("credit_contradiction_after_license", lambda d: by_id(d, "credits")[1][-1].__setattr__("tail", by_id(d, "credits")[1][-1].tail + " This is public domain; all obligations are waived."), meta, "credit_notices_exact")
    reject("credit_hidden_claim", lambda d: by_id(d, "credits")[2].append(ET.fromstring('<span>Native review has passed.</span>')), meta, "credit_notices_exact")
    reject("terminology_extra_paragraph", lambda d: by_id(d, "terminology").append(ET.fromstring('<p>وکھری دعویٰ</p>')), meta, "shared_terminology_complete_structure")
    reject("terminology_tail_injection", lambda d: by_id(d, "terminology").find("div/table/tbody/tr/td").__setattr__("tail", " وکھری دعویٰ"), meta, "shared_terminology_complete_structure")
    reject("bidi_control_injection", lambda d: by_id(d, "fs-id1165137892387").__setattr__("text", "\u202e"), validate_unicode, "reader_unicode_gate")
    return tested


def input_paths(manifest):
    language_files = ["source-excerpts/manifest-008.json", "source-excerpts/unit-008.cnxml", "translations/unit-008.json",
                      "qa/unit-008-language-notes.md", "provenance/unit-008-component-notices.json", "provenance/ATTRIBUTION.md",
                      "styles/reader.css", "terminology.tsv", "scripts/build.py", "scripts/prepare_unit_008.py",
                      "scripts/qa_notation.py", "scripts/qa_menu.py", "scripts/qa_toolkit.py", "assets/Figure_01_01_001.jpg"]
    result = [BASE / value for value in language_files]
    result.extend(BASE / "canon/receipts" / name for name in RECEIPTS)
    result.extend(BASE / image["path"] for image in manifest["images"])
    result.extend(BASE / "reader" / f"unit-{i:03}.html" for i in range(1, 8))
    result.extend(ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle" / image["source_path"] for image in manifest["images"])
    result.extend([ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle/media/CNX_Precalc_Figure_01_01_001.jpg",
                   ROOT / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv",
                   ROOT / manifest["source_byte_witnesses"]["canonical_checkout_path"],
                   ROOT / manifest["source_byte_witnesses"]["pinned_lf_witness_path"],
                   ROOT / manifest["source_byte_witnesses"]["comparison_path"]])
    return list(dict.fromkeys(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", choices=["008"], default="008")
    parser.add_argument("--check-only", action="store_true", help="Check the existing reader without a build or receipt write")
    arguments = parser.parse_args()
    manifest = json.loads((BASE / "source-excerpts/manifest-008.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    translation = json.loads((BASE / "translations/unit-008.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    notices = json.loads((BASE / "provenance/unit-008-component-notices.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    source = ET.parse(BASE / "source-excerpts/unit-008.cnxml").getroot()
    inputs = input_paths(manifest)
    initial = {path.relative_to(ROOT).as_posix(): sha256(path) for path in inputs}
    if not arguments.check_only:
        command = [sys.executable, "-B", str(BASE / "scripts/build.py"), "--unit", "008"]
        subprocess.run(command, check=True)
        first = READER.read_bytes()
        subprocess.run(command, check=True)
        require("two_builds_byte_identical", READER.read_bytes() == first)
    document = parse_reader(READER.read_text(encoding="utf-8"))
    checks = []

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    for path in inputs:
        if path.suffix in (".json", ".cnxml", ".md", ".py", ".css", ".tsv", ".html") and path.is_relative_to(BASE):
            check("Unicode_input:" + path.relative_to(BASE).as_posix(), FORBIDDEN.search(path.read_text(encoding="utf-8")) is None)
    validate_unicode(document, check)
    report = {"unit": "PNB-008", "source_boundary": validate_boundary(source, manifest, check),
              "structure": validate_structure(document, source, check),
              "blocks": validate_blocks(document, source, translation, check),
              "math": validate_math(document, source, check),
              "tables": validate_tables(document, source, translation, check),
              "links": validate_links(document, source, translation, manifest, check),
              "images": validate_images(document, source, translation, manifest, notices, check),
              "arithmetic": validate_arithmetic(document, source, check),
              "original_bridge": validate_bridge(document, source, translation, check),
              "metadata": validate_metadata(document, translation, manifest, check)}
    validate_directions(document, source, check)
    report["mutations"] = mutations(document, source, translation, manifest, notices, check)
    check("input_hashes_stable_during_run", initial == {path.relative_to(ROOT).as_posix(): sha256(path) for path in inputs})
    check("old_figure001_unmodified_copy", sha256(BASE / "assets/Figure_01_01_001.jpg")
          == sha256(ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle/media/CNX_Precalc_Figure_01_01_001.jpg"))
    report.update({"checks_passed": len(checks), "checks": checks, "mutation_count": len(report["mutations"]),
                   "inputs_sha256": initial, "reader_sha256": sha256(READER),
                   "two_builds_byte_identical": not arguments.check_only,
                   "normalization": "Only .cnxml file digests use CRLF-to-LF equivalence; source-byte checks separately verify the raw canonical checkout.",
                   "limits": ["The six-section selection excludes Section Exercises and does not complete the whole module or assigned books.",
                              "This is source-bound structural and arithmetic QA, not native Punjabi, educator, browser or screen-reader certification.",
                              "The 39 image-table pairs were actually read from pinned pixels; sampled arithmetic is not a proof of universal graph behavior.",
                              "Historical URLs, grades, balances and stock prices are source examples, not current availability or policy claims."]})
    if not arguments.check_only:
        (BASE / "qa/structural-008.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PNB-008: {len(checks)} checks passed; {len(report['mutations'])} detached mutations; {len(report['math']['edits'])} reversible MathML edits")


if __name__ == "__main__":
    main()
