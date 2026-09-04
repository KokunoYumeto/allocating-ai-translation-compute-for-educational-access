"""Source-bound PNB-007 QA; mutations only touch detached reader DOMs."""
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, unquote
from decimal import Decimal
import argparse
import copy
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from qa_notation import (MATH, LEDGER, signature, paths, at_path,
                         allowed_punctuation_edits, unique_object, jpeg_dimensions)
from qa_evaluation import (require, tag, text, compact, parents, by_id, parse_reader,
                           own_math, own_source_text, content_signature,
                           validate_directions, FORBIDDEN)

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
READER = BASE / "reader/unit-007.html"
CNXML = "http://cnx.rice.edu/cnxml"
SELECTED = ["fs-id1165137591827", "fs-id1165137648450", "fs-id1165135696152"]
NEXT = "fs-id1165135422920"
BLOCKS = {"figure", "para", "note", "list", "exercise", "problem", "solution",
          "section", "equation", "example", "table", "footnote"}
NUMERIC_SUFFIXES = {
    ("fs-id1165137584852", 2): ("mn", "2160."),
    ("fs-id1165137653327/item/2", 0): ("mn", "6."),
    ("fs-id1165137725812/item/1", 2): ("mn", "3."),
    ("fs-id1165137725812/item/1", 4): ("mn", "7."),
    ("fs-id1165137725812/item/2", 3): ("mn", "4."),
    ("fs-id1165137604039/item/2", 0): ("mn", "4."),
    ("fs-id1165137871522/item/1", 3): ("mn", "1."),
    ("fs-id1165137871522/item/2", 0): ("mn", "4,"),
    ("fs-id1165137871522/item/2", 3): ("mn", "4:"),
    ("fs-id1165137871522/item/2", 6): ("mn", "4:"),
    ("fs-id1165137871522/item/2", 8): ("mn", "3."),
    ("fs-id1165137871522/item/2", 12): ("mtext", "3,"),
    ("fs-id1165137695208", 0): ("mn", "1."),
}
PET_CELLS = [f"Table_01_01_10/row/{row}/entry/1" for row in range(2, 7)]
ALT_NOTES = {"fs-id1165137705894": "representations-alt-wording",
             "fs-id1165135675165": "representations-alt-wording",
             "fs-id1165137469773": "representations-alt-vertex"}


def sha256(path):
    data = path.read_bytes()
    if path.suffix == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def source_specs(source):
    result = {}

    def visit(node, parent=None, index=0):
        name = tag(node)
        if name == "equation":
            return
        if name == "media":
            result[node.get("id") + "/alt"] = node
            return
        if name == "table":
            result[node.get("id") + "/summary"] = node
            for ri, row in enumerate([n for n in node.iter() if tag(n) == "row"], 1):
                for ci, entry in enumerate(row, 1):
                    if any(char.isalpha() for char in text(entry)):
                        result[f'{node.get("id")}/row/{ri}/entry/{ci}'] = entry
            return
        if name in ("para", "title", "label", "caption", "item", "footnote"):
            key = (f'{parent.get("id")}/item/{index + 1}' if name == "item"
                   else node.get("id") or f'{parent.get("id")}/{name}')
            result[key] = node
            for position, child in enumerate(node):
                if tag(child) in BLOCKS:
                    visit(child, node, position)
            return
        for position, child in enumerate(node):
            visit(child, node, position)

    visit(source)
    return result


def target_block(document, source, key, node):
    if tag(node) == "entry":
        table_id, _, ri, _, ci = key.split("/")
        return by_id(document, table_id).findall("./tbody/tr")[int(ri) - 1][int(ci) - 1]
    if tag(node) == "footnote":
        return by_id(document, node.get("id") + "-text")
    if node.get("id"):
        return by_id(document, node.get("id"))
    parent = parents(source)[node]
    target = by_id(document, parent.get("id"))
    if tag(node) == "item":
        return target.findall("li")[list(parent).index(node)]
    heading = "h2" if tag(node) == "title" and tag(parent) == "section" else "h3"
    require("one_source_heading:" + key, len(target.findall(heading)) == 1)
    return target.find(heading)


def validate_boundary(source, manifest, check=require):
    witnesses = manifest["source_byte_witnesses"]
    checkout = WORKSPACE / witnesses["canonical_checkout_path"]
    pinned = WORKSPACE / witnesses["pinned_lf_witness_path"]
    comparison = WORKSPACE / witnesses["comparison_path"]
    check("raw_checkout_hash", hashlib.sha256(checkout.read_bytes()).hexdigest() == witnesses["canonical_checkout_sha256"])
    check("pinned_lf_hash", sha256(pinned) == manifest["full_module_sha256"])
    check("newline_only_checkout_equivalence", checkout.read_bytes().replace(b"\r\n", b"\n") == pinned.read_bytes())
    check("comparison_hash", hashlib.sha256(comparison.read_bytes()).hexdigest() == witnesses["comparison_sha256"])
    full = ET.parse(pinned).getroot()
    outer = by_id(full, "fs-id1165137503241")
    originals = list(outer)[4:]
    check("three_remaining_direct_sections", len(originals) == 3 and [n.get("id") for n in originals] == SELECTED)
    check("complete_three_subtree_witnesses", len(source) == 3 and all(
        signature(left) == signature(right) and left.tail == right.tail
        for left, right in zip(originals, source)))
    check("manifest_selection", manifest["selection_ids"] == SELECTED and manifest["next_source_id"] == NEXT)
    p = parents(full)[outer]
    check("next_outer_section", list(p)[list(p).index(outer) + 1].get("id") == NEXT)
    boundary = manifest["selection_boundary"]
    expected = [{"index": i + 5, "tag": "section", "id": sid, "coverage": "complete subtree"}
                for i, sid in enumerate(SELECTED)]
    check("manifest_explicit_child_boundary", boundary["outer_section_id"] == outer.get("id")
          and boundary["included_direct_children"] == expected
          and boundary["last_selected_descendant_id"] == "fs-id1165137598287"
          and boundary["following_complete_outer_section_id"] == NEXT)
    return {"outer_section": outer.get("id"), "selected_children": expected, "next_source_id": NEXT}



def validate_structure(document, source, check=require):
    ids = [n.get("id") for n in document.iter() if n.get("id")]
    originals = [n for n in source.iter() if n is not source and n.get("id")]
    source_ids = [n.get("id") for n in originals]
    check("unique_reader_ids", len(ids) == len(set(ids)))
    check("84_source_ids_exact_order", len(source_ids) == 84 and [i for i in ids if i in source_ids] == source_ids)
    check("no_repeated_outer_wrapper", source.get("id") not in ids and "fs-id1165137503241" not in ids)
    op, rp = parents(source), parents(document)

    def chain(node, p):
        values = []
        while node in p:
            node = p[node]
            if node.get("id") in source_ids:
                values.append(node.get("id"))
        return values

    check("all_source_id_ancestry", all(chain(n, op) == chain(by_id(document, n.get("id")), rp) for n in originals))
    main = document.find("body/main")
    expected_main = [("aside", "representations-source-context"), ("p", None),
                     *[("section", sid) for sid in SELECTED], ("section", None),
                     ("section", "representations-bridge"), ("section", "terminology")]
    check("complete_main_child_sequence", [(n.tag, n.get("id")) for n in main] == expected_main)
    check("main_label_and_endnotes", main[1].get("class") == "source-label" and main[5].get("class") == "source-endnotes")
    check("main_no_unkeyed_text", not (main.text or "").strip() and all(not (n.tail or "").strip() for n in main))
    structural = {"section", "example", "exercise", "problem", "solution", "commentary", "note", "list", "figure"}
    output = {"section": "section", "example": "section", "exercise": "div", "problem": "div",
              "solution": "section", "commentary": "div", "note": "aside", "list": "ol",
              "figure": "figure", "para": "p", "item": "li", "equation": "div", "label": "h3"}
    for original in (n for n in source.iter() if tag(n) in structural):
        target = by_id(document, original.get("id"))
        expected_attrs = {"id": original.get("id")}
        if tag(original) == "section":
            expected_attrs["class"] = "translated"
        elif tag(original) in ("example", "exercise", "problem", "solution", "commentary"):
            expected_attrs["class"] = "source-" + tag(original)
        elif tag(original) == "list" and any(c.get("class") == "token" for item in original for c in item):
            expected_attrs.update({"class": "source-parts", "role": "list"})
        check("source_container_tag_attributes:" + original.get("id"),
              target.tag == output[tag(original)] and target.attrib == expected_attrs)
        expected = []
        if tag(original) == "example":
            expected.append(("h2", None))
            number = int(original.get("id").rsplit("_", 1)[-1])
            heading = ET.fromstring(f'<h2>حل کیتی مثال <bdi dir="ltr">{number}</bdi></h2>')
            check("automatic_example_heading:" + original.get("id"), signature(target[0]) == signature(heading))
        elif tag(original) == "solution":
            expected.append(("h3", None))
            check("automatic_solution_heading:" + original.get("id"), signature(target[0]) == signature(ET.fromstring("<h3>حل</h3>")))
        for child in original:
            name = tag(child)
            if name == "media":
                expected.extend([("div", None), ("p", None), ("p", None)])
            elif name == "table":
                expected.append(("div", None))
            else:
                target_tag = ("h2" if tag(original) == "section" else "h3") if name == "title" else output[name]
                expected.append((target_tag, child.get("id")))
        check("complete_structural_children:" + original.get("id"), [(n.tag, n.get("id")) for n in target] == expected)
        check("no_structural_text_or_tail:" + original.get("id"), target.text in (None, "") and all(n.tail in (None, "") for n in target))
        check("no_source_container_prose_omitted:" + original.get("id"),
              not (original.text or "").strip() and all(not (n.tail or "").strip() for n in original))
    examples = [n.get("id") for n in source.iter() if tag(n) == "example"]
    check("examples09_to12", examples == [f"Example_01_01_{i:02}" for i in range(9, 13)])
    pairings = []
    for exercise in (n for n in source.iter() if tag(n) == "exercise"):
        expected = [(tag(n), n.get("id")) for n in exercise]
        target = by_id(document, exercise.get("id"))
        check("exercise_pairing:" + exercise.get("id"),
              [(n.get("class").removeprefix("source-"), n.get("id")) for n in target] == expected)
        check("problem_solution_first:" + exercise.get("id"), [name for name, _ in expected[:2]] == ["problem", "solution"])
        pairings.append({"exercise": exercise.get("id"), "children": expected})
    check("seven_exercises_one_analysis", len(pairings) == 7
          and [tag(n) for n in by_id(source, "fs-id1165137634899")] == ["problem", "solution", "commentary"])
    for original in (n for n in source.iter() if tag(n) == "list"):
        target = by_id(document, original.get("id"))
        check("list_length:" + original.get("id"), len(original) == len(target))
        if any(c.get("class") == "token" for item in original for c in item):
            check("circled_list_semantics:" + original.get("id"), target.get("class") == "source-parts" and target.get("role") == "list")
            for i, item in enumerate(target):
                check(f"part_label:{original.get('id')}:{i}", item[0].tag == "bdi"
                      and item[0].get("dir") == "ltr" and text(item[0]) == f"({chr(97+i)})")
    return source_ids, pairings


def validate_blocks(document, source, translation, manifest, check=require):
    specs = source_specs(source)
    blocks = translation["source_blocks"]
    check("72_exact_keys_in_order", len(specs) == len(blocks) == 72 and list(specs) == list(blocks))
    labels = {e["figure_id"]: e["local_label"] for e in manifest["images"]}
    labels.update({e["id"]: e["local_label"] for e in manifest["references"]})
    totals, numerals = {"math": 0, "link": 0, "child": 0}, {}
    for key, original in specs.items():
        target = target_block(document, source, key, original)
        value, name = blocks[key], tag(original)
        if name in ("table", "media"):
            attr = "data-source-summary" if name == "table" else "data-source-alt"
            check("faithful_source_attribute:" + key, target.get(attr) == value)
            original_prose, visible = original.get("summary" if name == "table" else "alt"), value
        else:
            if name != "entry":
                parent = parents(source)[original]
                expected_tag = {"para": "p", "item": "li", "label": "h3", "caption": "figcaption",
                                "footnote": "li", "title": "h2" if tag(parent) == "section" else "h3"}[name]
                expected_attrs = ({"id": original.get("id") + "-text"} if name == "footnote"
                                  else {"id": original.get("id")} if original.get("id") else {})
                check("source_block_tag_attributes:" + key, target.tag == expected_tag and target.attrib == expected_attrs)
            maths, links = own_math(original), [c for c in original if tag(c) == "link"]
            children = [c for c in original if tag(c) in BLOCKS]
            for kind, nodes in (("math", maths), ("link", links), ("child", children)):
                check(f"ordered_{kind}_slots:{key}", [int(i) for i in re.findall(r"\{\{" + kind + r":(\d+)\}\}", value)] == list(range(len(nodes))))
                totals[kind] += len(nodes)
            child_ids = [n.get("id") for n in children]
            expected = re.sub(r"\{\{(math|child):(\d+)\}\}", r'<slot kind="\1" index="\2" />', value)

            def link_markup(match):
                sid = links[int(match[1])].get("target-id")
                noun = "جدول" if sid.startswith("Table_") else "شکل"
                return f'<a href="#{sid}">{noun} <bdi dir="ltr">{labels[sid]}</bdi></a>'

            expected = re.sub(r"\{\{link:(\d+)\}\}", link_markup, expected)
            expected = ET.fromstring("<fragment>" + expected + "</fragment>")
            actual = copy.deepcopy(target)
            if name == "footnote":
                check("endnote_exact_backlink", len(actual) > 1 and actual[-1].tag == "a"
                      and actual[-1].attrib == {"href": "#" + original.get("id")} and text(actual[-1]) == "متن ول واپس"
                      and len(actual[-1]) == 0 and actual[-1].tail in (None, "") and actual[-2].tail == " ")
                actual.remove(actual[-1])
                actual[-1].tail = None
            count = [0]

            def slots(node):
                for i, child in enumerate(list(node)):
                    replacement = None
                    if child.get("id") in child_ids:
                        replacement = ET.Element("slot", {"kind": "child", "index": str(child_ids.index(child.get("id")))})
                    elif child.get("class") == "math-isolate":
                        replacement = ET.Element("slot", {"kind": "math", "index": str(count[0])})
                        count[0] += 1
                    else:
                        slots(child)
                    if replacement is not None:
                        replacement.tail = child.tail
                        node.remove(child)
                        node.insert(i, replacement)

            slots(actual)
            check("exact_fragment_and_nested_slots:" + key, content_signature(actual) == content_signature(expected))
            check("own_math_slot_count:" + key, count[0] == len(maths))
            clean = ET.fromstring("<fragment>" + re.sub(r"\{\{(?:math|link|child):\d+\}\}", "", value) + "</fragment>")
            original_prose, visible = own_source_text(original), text(clean)
            source_terms = [n.get("id") for n in original.iter() if tag(n) == "term"]
            check("inline_term_ids:" + key, [n.get("id") for n in clean.iter() if n.get("id")] == source_terms)
            emphasis = ["em" if n.get("effect") == "italics" else "strong" for n in original if tag(n) == "emphasis"]
            check("source_emphasis:" + key, [n.tag for n in target if n.tag in ("em", "strong")] == emphasis)
        digits = re.findall(r"\d+(?:\.\d+)?", original_prose)
        check("prose_numbers_preserved:" + key, re.findall(r"\d+(?:\.\d+)?", visible) == digits)
        if digits:
            numerals[key] = digits
    check("79_math_6_links_3_children", totals == {"math": 79, "link": 6, "child": 3})
    return specs, numerals, totals


def permitted_edits(original, context):
    allowed = allowed_punctuation_edits(original)
    if context in NUMERIC_SUFFIXES:
        leaf_path, leaf = [(p, n) for p, n in paths(original) if not len(n)][-1]
        expected_tag, old = NUMERIC_SUFFIXES[context]
        require("numeric_suffix_exact_source_position:" + str(context), tag(leaf) == expected_tag
                and leaf.text == old and re.fullmatch(r"[0-9]+[.,:]", old) is not None)
        new = old[:-1]
        require("numeric_suffix_semantics", Decimal(new) == Decimal(old.rstrip(".,:")))
        allowed[leaf_path] = (old, new)
    return allowed


def restore_math(original, rendered, context):
    require("math_root_ltr:" + str(context), rendered.get("dir") == "ltr")
    require("source_no_presentation_metadata", "dir" not in original.attrib and LEDGER not in original.attrib)
    raw = rendered.get(LEDGER)
    try:
        entries = [] if raw is None else json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise AssertionError("ledger_valid_json") from error
    require("ledger_nonempty_list_when_present", isinstance(entries, list) and (raw is None or bool(entries)))
    allowed, restored, seen = permitted_edits(original, context), copy.deepcopy(rendered), set()
    for entry in entries:
        require("ledger_exact_schema", isinstance(entry, dict) and set(entry) == {"path", "old", "new"}
                and isinstance(entry["path"], list) and all(type(i) is int and i >= 0 for i in entry["path"])
                and isinstance(entry["old"], str) and isinstance(entry["new"], str))
        path = tuple(entry["path"])
        require("ledger_path_unique", path not in seen)
        seen.add(path)
        require("source_position_whitelist", path in allowed)
        before, after = allowed[path]
        source_leaf, target_leaf = at_path(original, path), at_path(restored, path)
        require("ledger_old_equals_source", entry["old"] == before == source_leaf.text)
        require("ledger_new_equals_policy", entry["new"] == after)
        require("ledger_new_equals_rendered", target_leaf.text == after or (after == "" and target_leaf.text is None))
        require("edited_leaf_topology", source_leaf.tag == target_leaf.tag and len(source_leaf) == len(target_leaf) == 0)
        target_leaf.text = before
    require("complete_expected_ledger", seen == set(allowed))
    restored.attrib.pop("dir")
    restored.attrib.pop(LEDGER, None)
    require("exact_math_reconstruction", signature(restored) == signature(original))
    return entries



def math_contexts(document, source, rendered=False):
    specs = source_specs(source)
    mapping = ({target_block(document, source, key, node): key for key, node in specs.items()}
               if rendered else {node: key for key, node in specs.items()})
    for equation in (n for n in source.iter() if tag(n) == "equation"):
        mapping[by_id(document, equation.get("id")) if rendered else equation] = equation.get("id")
    root = document if rendered else source
    p = parents(root)
    result, counts = [], {}
    for math_node in root.iter("{" + MATH + "}math"):
        node = math_node
        while node in p:
            node = p[node]
            if node in mapping:
                owner = mapping[node]
                slot = counts.get(owner, 0)
                result.append((owner, slot))
                counts[owner] = slot + 1
                break
        else:
            raise AssertionError("math_has_source_owner")
    return result


def validate_math(document, source, check=require):
    originals = list(source.iter("{" + MATH + "}math"))
    rendered = [n for n in document.iter() if tag(n) == "math"]
    check("83_exact_namespace_math_trees", len(originals) == len(rendered) == 83
          and all(n.tag == "{" + MATH + "}math" for n in rendered))
    contexts = math_contexts(document, source)
    check("all_math_owners_slots_exact", contexts == math_contexts(document, source, True))
    edits, english, numeric = [], [], []
    p = parents(document)
    for i, (original, target, context) in enumerate(zip(originals, rendered, contexts)):
        wrapper = p[target]
        check(f"math_wrapper_ltr:{i}", wrapper.tag == "span" and wrapper.get("class") == "math-isolate" and wrapper.get("dir") == "ltr")
        check(f"math_wrapper_pure:{i}", len(wrapper) == 1 and wrapper[0] is target
              and wrapper.text in (None, "") and target.tail in (None, ""))
        wrapper_attrs = {"class": "math-isolate", "dir": "ltr"}
        if original.get("display") == "block":
            wrapper_attrs.update({"tabindex": "0", "role": "region", "aria-label": "ریاضی دا فارمولا؛ لوڑ پئے تے پاسے سرکاؤ"})
        check(f"math_wrapper_attributes_exact:{i}", wrapper.attrib == wrapper_attrs)
        entries = restore_math(original, target, context)
        check(f"exact_math_tree:{i}", True)
        edits.extend({"tree": i, "owner": context[0], "slot": context[1], **entry} for entry in entries)
        if context in NUMERIC_SUFFIXES:
            numeric.append({"owner": context[0], "slot": context[1], "source_token": NUMERIC_SUFFIXES[context]})
        for path, leaf in paths(original):
            if tag(leaf) == "mtext" and re.search("[A-Za-z]", leaf.text or ""):
                check(f"english_mtext_exact:{i}:{path}", at_path(target, path).text == leaf.text)
                english.append(leaf.text)
    equations = [n for n in source.iter() if tag(n) == "equation"]
    check("four_display_equations", len(equations) == 4 and sum(n.get("display") == "block" for n in rendered) == 4)
    for original in equations:
        target = by_id(document, original.get("id"))
        check("equation_container_pure:" + original.get("id"), target.tag == "div" and target.get("dir") == "ltr"
              and len(target) == 1 and target[0].get("class") == "math-isolate"
              and target.text in (None, "") and target[0].tail in (None, "")
              and target[0].get("role") == "region" and target[0].get("tabindex") == "0")
    check("ledgers_only_on_math_roots", all(n in rendered for n in document.iter() if LEDGER in n.attrib))
    check("13_exact_numeric_suffix_positions", len(numeric) == 13 and set(NUMERIC_SUFFIXES).issubset(contexts))
    check("41_source_derived_edge_edits", len(edits) == 41)
    check("four_table_header_math_owners", len([c for c in contexts if c[0].startswith("Table_")]) == 4)
    return {"trees": 83, "inline_trees": 79, "equations": 4, "text_edits": edits,
            "numeric_suffixes": numeric, "source_contexts": contexts, "english_mtext": english}


def validate_tables(document, source, translation, manifest, check=require):
    originals = [n for n in source.iter() if tag(n) == "table"]
    check("three_source_tables", [n.get("id") for n in originals] == [f"Table_01_01_{i}" for i in (10, 11, 12)])
    check("five_explicit_translated_data_cells", translation["translated_table_data_cells"] == PET_CELLS)
    check("one_corrected_summary", set(translation["table_summary_overrides"]) == {"Table_01_01_10"})
    report = []
    op, rp = parents(source), parents(document)
    for original in originals:
        sid = original.get("id")
        target = by_id(document, sid)
        summary = translation["source_blocks"][sid + "/summary"]
        expected_attrs = {"id": sid, "aria-label": translation["table_summary_overrides"].get(sid, summary),
                          "data-source-summary": summary, "dir": "ltr", "class": "source-table"}
        check("table_attributes_exact:" + sid, target.attrib == expected_attrs)
        check("table_summary_exact:" + sid, target.get("data-source-summary") == summary
              and target.get("aria-label") == translation["table_summary_overrides"].get(sid, summary))
        check("table_structure_pure:" + sid, target.tag == "table" and target.get("dir") == "ltr"
              and len(target) == 1 and target[0].tag == "tbody" and target.text in (None, "") and target[0].tail in (None, ""))
        wrapper = rp[target]
        check("table_wrapper_ltr_focus:" + sid, wrapper.get("class") == "table-scroll source-table-scroll"
              and wrapper.get("dir") == "ltr" and wrapper.get("tabindex") == "0" and wrapper.get("role") == "region")
        check("table_wrapper_pure:" + sid, len(wrapper) == 1 and wrapper[0] is target
              and wrapper.text in (None, "") and target.tail in (None, ""))
        check("table_wrapper_attributes_exact:" + sid, wrapper.attrib == {"class": "table-scroll source-table-scroll",
              "dir": "ltr", "tabindex": "0", "role": "region", "aria-label": "جدول؛ لوڑ پئے تے پاسے سرکاؤ"})
        source_rows = [n for n in original.iter() if tag(n) == "row"]
        rows = list(target[0])
        check("table_rows_exact:" + sid, len(source_rows) == len(rows) and all(n.tag == "tr" for n in rows)
              and target[0].text in (None, "") and all(n.tail in (None, "") for n in rows))
        check("table_body_row_attributes_exact:" + sid, target[0].attrib == {} and all(row.attrib == {} for row in rows))
        columns = int(next(n for n in original if tag(n) == "tgroup").get("cols"))
        matrix = []
        for ri, (sr, tr) in enumerate(zip(source_rows, rows), 1):
            check(f"row_shape:{sid}:{ri}", len(sr) == len(tr) == columns and tr.text in (None, "")
                  and all(n.tail in (None, "") for n in tr))
            row_values = []
            for ci, (entry, cell) in enumerate(zip(sr, tr), 1):
                key = f"{sid}/row/{ri}/entry/{ci}"
                is_data = key in PET_CELLS
                header = tag(op[sr]) == "thead" or (sid in ("Table_01_01_11", "Table_01_01_12") and ci == 1)
                expected_tag = "th" if header else "td"
                check("cell_semantics:" + key, cell.tag == expected_tag and cell.get("scope")
                      == (("col" if tag(op[sr]) == "thead" else "row") if header else None))
                if header or is_data:
                    check("translated_cell_key_direction:" + key, key in translation["source_blocks"] and cell.get("dir") == "rtl")
                else:
                    check("numeric_cell_source_exact:" + key, len(cell) == 0 and cell.text == text(entry)
                          and cell.get("dir") == "ltr" and key not in translation["source_blocks"])
                if entry.get("align") == "center":
                    check("source_cell_center_alignment:" + key, cell.get("style") == "text-align:center")
                expected_cell_attrs = {"dir": "rtl" if header or is_data else "ltr"}
                if header:
                    expected_cell_attrs["scope"] = "col" if tag(op[sr]) == "thead" else "row"
                if entry.get("align") == "center":
                    expected_cell_attrs["style"] = "text-align:center"
                check("cell_attributes_exact:" + key, cell.attrib == expected_cell_attrs)
                row_values.append(text(cell))
            matrix.append(row_values)
        report.append({"id": sid, "rows": len(rows), "columns": columns, "rendered_cells": matrix})
    table10 = by_id(document, "Table_01_01_10")
    check("2100_only_in_retained_summary", "2100" in table10.get("data-source-summary")
          and "2100" not in table10.get("aria-label") and "2160" in table10.get("aria-label"))
    check("actual_goldfish_2160", table10.findall("./tbody/tr")[4][1].text == "2160")
    table12 = by_id(source, "Table_01_01_12")
    check("unnumbered_table12_source_and_no_reference", table12.get("class") == "unnumbered"
          and len([n for n in table12 if tag(n) == "label"]) == 1
          and not text(next(n for n in table12 if tag(n) == "label"))
          and [n["id"] for n in manifest["references"]] == ["Table_01_01_10", "Table_01_01_11"])
    check("no_invented_table12_caption_or_link", not by_id(document, "Table_01_01_12").findall("caption")
          and not any(n.get("href") == "#Table_01_01_12" for n in document.iter("a")))
    return report


def validate_links(document, source, translation, manifest, check=require):
    labels = {e["figure_id"]: e["local_label"] for e in manifest["images"]}
    labels.update({e["id"]: e["local_label"] for e in manifest["references"]})
    count = 0
    for key, original in source_specs(source).items():
        links = [n for n in original if tag(n) == "link"]
        if not links:
            continue
        target = target_block(document, source, key, original)
        actual = target.findall("a")
        check("source_link_count:" + key, len(actual) == len(links))
        for left, right in zip(links, actual):
            sid = left.get("target-id")
            expected = ET.fromstring(f'<a href="#{sid}">{"جدول" if sid.startswith("Table_") else "شکل"} <bdi dir="ltr">{labels[sid]}</bdi></a>')
            check("source_link_exact:" + key, signature(right) == signature(expected))
            count += 1
    check("six_source_links", count == 6)
    sid = "fs-id1165135434830"
    source_note = by_id(source, sid)
    ref, body = by_id(document, sid), by_id(document, sid + "-text")
    expected = ET.fromstring(f'<sup id="{sid}" class="source-footnote"><a href="#{sid}-text" aria-label="ماخذ دا حوالہ 1"><bdi dir="ltr">1</bdi></a></sup>')
    check("source_footnote_sup_exact", signature(ref) == signature(expected))
    url = re.search(r"https?://\S+", text(source_note))[0].rstrip(".")
    date = re.search(r"\d+/\d+/\d+", text(source_note))[0]
    external = [n for n in body.iter("a") if n.get("href", "").startswith("http")]
    check("footnote_original_URL_and_date", len(external) == 1 and external[0].get("href") == url
          and text(external[0]) == url and date in text(body))
    endnotes = next(n for n in document.iter() if n.get("class") == "source-endnotes")
    check("endnote_container_pure", [n.tag for n in endnotes] == ["h2", "ol"] and text(endnotes[0]) == "ماخذ دے حوالے"
          and endnotes.attrib == {"class": "source-endnotes"} and endnotes[0].attrib == endnotes[1].attrib == {}
          and len(endnotes[0]) == 0 and len(endnotes[1]) == 1 and endnotes[1][0] is body
          and endnotes.text in (None, "") and all(n.tail in (None, "") for n in endnotes)
          and endnotes[1].text in (None, "") and body.tail in (None, ""))
    local = []
    for node in document.iter():
        for attr in ("href", "src"):
            if attr not in node.attrib:
                continue
            value = node.get(attr)
            parsed = urlsplit(value)
            if parsed.scheme in ("http", "https", "mailto"):
                continue
            check("local_scheme:" + value, not parsed.scheme and not parsed.netloc)
            path = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            check("local_file:" + value, path.is_file())
            if parsed.fragment:
                other = document if path == READER.resolve() else parse_reader(path.read_text(encoding="utf-8"))
                by_id(other, unquote(parsed.fragment))
            local.append(value)
    check("previous_unit006_navigation", any(n.get("href") == "unit-006.html" for n in document.findall(".//nav/a")))
    return {"source_link_count": count, "footnote_url": url, "footnote_date": date, "local_references": local}



def arithmetic(node, values):
    name = tag(node)
    if name == "mn":
        return float((node.text or "").rstrip(".,:"))
    if name == "mi":
        return values[node.text]
    if name == "msup":
        return arithmetic(node[0], values) ** arithmetic(node[1], values)
    if name == "mfrac":
        return arithmetic(node[0], values) / arithmetic(node[1], values)
    if name == "msqrt":
        return math.sqrt(arithmetic_sequence(list(node), values))
    if name == "mroot":
        require("real_cube_root_degree", arithmetic(node[1], values) == 3)
        return math.cbrt(arithmetic(node[0], values))
    require("supported_arithmetic_node", name in ("math", "mrow"))
    return arithmetic_sequence(list(node), values)


def arithmetic_sequence(nodes, values):
    pieces, previous = [], "op"
    for node in nodes:
        if tag(node) == "mtext" and not (node.text or "").strip():
            continue
        if tag(node) == "mo":
            token = (node.text or "").replace("−", "-")
            if token in ("", ".", ",", ":"):
                continue
            kind = "close" if token == ")" else "open" if token == "(" else "op"
        else:
            token, kind = repr(arithmetic(node, values)), "value"
        if previous in ("value", "close") and kind in ("value", "open"):
            pieces.append("*")
        pieces.append(token)
        previous = kind
    expression = "".join(pieces)
    require("arithmetic_numeric_only", re.fullmatch(r"[0-9eE+*/(). -]+", expression) is not None)
    return eval(expression, {"__builtins__": {}}, {})


def equation_rhs(node):
    row = list(node[0])
    index = max(i for i, child in enumerate(row) if tag(child) == "mo" and child.text == "=")
    return row[index + 1:]


def formula(root, sid, slot=0):
    return list(by_id(root, sid).iter("{" + MATH + "}math"))[slot]


def validate_mathematics(document, source, check=require):
    linear_id, cube_id = "fs-id1165135187787", "fs-id1165135344102"
    for variable in (-12, -3, 0, 3, 12):
        expected = arithmetic_sequence(equation_rhs(formula(source, linear_id)), {"n": variable})
        actual = arithmetic_sequence(equation_rhs(formula(document, linear_id)), {"n": variable})
        check("linear_source_target:" + str(variable), math.isclose(expected, actual))
        source_left = list(formula(source, "fs-id1165137452465")[0])[:5]
        check("linear_original_relation:" + str(variable), math.isclose(arithmetic_sequence(source_left, {"n": variable, "p": actual}), 12))
    cube_samples = []
    for x in (-64, -8, 0, 1, 8, 64):
        expected = arithmetic_sequence(equation_rhs(formula(source, cube_id)), {"x": x})
        actual = arithmetic_sequence(equation_rhs(formula(document, cube_id)), {"x": x})
        check("real_cube_root_answer:" + str(x), math.isclose(expected, actual) and math.isclose(x - 8 * actual ** 3, 0, abs_tol=1e-9))
        cube_samples.append([x, actual])
    for root, label in ((source, "source"), (document, "reader")):
        lhs = list(formula(root, "fs-id1165137758151")[0])[:3]
        check("circle_two_outputs_at_zero:" + label, arithmetic_sequence(lhs, {"x": 0, "y": 1})
              == arithmetic_sequence(lhs, {"x": 0, "y": -1}) == 1)
        check("circle_endpoints:" + label, all(arithmetic_sequence(lhs, {"x": x, "y": 0}) == 1 for x in (-1, 1)))
    tables = {}
    for sid in ("Table_01_01_11", "Table_01_01_12"):
        sr = [n for n in by_id(source, sid).iter() if tag(n) == "row"]
        tr = by_id(document, sid).findall("./tbody/tr")
        original = dict(zip([int(text(n)) for n in list(sr[0])[1:]], [int(text(n)) for n in list(sr[1])[1:]]))
        rendered = dict(zip([int(text(n)) for n in list(tr[0])[1:]], [int(text(n)) for n in list(tr[1])[1:]]))
        check("table_map_source_exact:" + sid, original == rendered)
        check("g3_and_g1_answers:" + sid, rendered[3] == 7 and rendered[1] == 8)
        check("g6_two_solutions:" + sid, [n for n in rendered if rendered[n] == 6] == [2, 4])
        tables[sid] = list(rendered.items())
    check("tabular_tryit_actual_answer", compact(text(formula(document, "fs-id1165137423937"))) == "g(1)=8")
    check("graph_tryit_two_answers", [compact(text(n)) for n in own_math(by_id(document, "fs-id1165137598287"))] == ["x=0", "x=2"])
    graph_answers = by_id(document, "fs-id1165137871522").findall("li")
    graph_values = [compact(text(n)).rstrip(".,:") for n in own_math(graph_answers[1])]
    check("graph_source_solution_values", graph_values[4:6] == ["(−1,4)", "(3,4)"]
          and graph_values[7:11] == ["−1", "3", "f(−1)=4", "f(3)=4"])
    check("graph_evaluation_answer", compact(text(own_math(graph_answers[0])[3])) == "f(2)=1")
    implicit = []
    for y in (-4, -2, 0, 2, 4):
        expected = arithmetic_sequence(equation_rhs(formula(source, "fs-id1165137627784")), {"y": y})
        actual = arithmetic_sequence(equation_rhs(formula(document, "fs-id1165137627784")), {"y": y})
        check("implicit_formula_source_target:" + str(y), actual == expected)
        implicit.append(actual)
    check("implicit_sample_monotonicity", all(a < b for a, b in zip(implicit, implicit[1:])))
    pet_rows = by_id(document, "Table_01_01_10").findall("./tbody/tr")
    pets = [float(text(row[1])) for row in pet_rows[1:]]
    check("pet_formula_source_cell", compact(text(formula(document, "fs-id1165137584852", 2))) == "P(goldfish)=" + str(int(pets[3])))
    check("source_hours_original_rounding", math.isclose(pets[0] * 3600, 28.8) and math.isclose(pets[1] * 60, 4.98))
    return {"cube_root_samples": cube_samples, "table_pairs": tables, "pet_values": pets,
            "implicit_sample_outputs": implicit,
            "claim": "Bounded arithmetic checks are not universal proofs or verification of animal science. Raster reading remains a separate inspection."}


def validate_bridge(document, source, translation, check=require):
    selected = [by_id(document, sid) for sid in SELECTED]
    selected_nodes = {n for root in selected for n in root.iter()}
    rp = parents(document)
    for field in ("bridge_before_html", "bridge_after_html"):
        original = ET.fromstring(translation[field])
        actual = by_id(document, original.get("id"))
        check("original_fragment_exact:" + field, signature(actual) == signature(original))
        check("original_separate_from_source:" + field, actual not in selected_nodes
              and rp[actual] is rp[selected[0]] and actual.get("data-origin") == "original-bridge")
    check("no_original_inside_source", not any(n.get("data-origin") == "original-bridge" for n in selected_nodes))
    bridge = by_id(document, "representations-bridge")
    bdis = {compact(text(n)) for n in bridge.iter("bdi")}
    for expression in ("p=f(n)=2−n/3", "x²+y²=1", "x=0", "y=1", "y=−1", "x=−1", "x=1", "y=0",
                       "−1≤x≤1", "+√(1−x²)", "−√(1−x²)", "y=∛x/2", "x=−8", "x−8y³=0",
                       "x=y+2ʸ", "P(goldfish)=2160", "0.008", "28.8", "0.083", "4.98",
                       "{0.008,0.083,16,2160,3600}", "g(3)=7", "g(1)=8", "g(n)=6", "n=2", "n=4",
                       "(1,0)", "(0,1)", "(−1,4)", "(3,4)", "f(2)=1", "x=2", "x=3"):
        check("precision_formula_present:" + expression, expression in bdis)
    check("nonzero_and_historical_original_notes", "غیر صفر" in text(bridge)
          and "نویں سائنسی" in text(by_id(document, "representations-source-context"))
          and "غیر صفر" not in "".join(text(n) for n in selected))
    english = {re.sub(r"\s+", " ", text(n)) for n in bridge.iter("bdi") if n.get("lang") == "en"}
    check("source_English_keys", {"expression involving n", "Subtract 2n from both sides.",
          "Divide both sides by 6 and simplify.", "and", "goldfish", "beta fish"}.issubset(english))
    source_words = {re.sub(r"\s+", " ", n.text or "").strip() for n in source.iter("{" + MATH + "}mtext")
                    if re.search("[A-Za-z]", n.text or "")}
    check("English_keys_bound_to_source", source_words == {"expression", "involving", "Subtract", "from both sides",
          "Divide both sides by 6 and simplify", "and", "goldfish"})
    check("alt_note_mapping_exact", translation["image_alt_note_ids"] == ALT_NOTES)
    for mid, note_id in ALT_NOTES.items():
        note = by_id(document, note_id)
        check("alt_correction_original_location:" + mid, note in set(bridge.iter()) and "(1,0)" in compact(text(note)))
    check("vertex_error_disclosed", "(0,1)" in compact(text(by_id(document, "representations-alt-vertex"))))
    return {"source_English_mtext": sorted(source_words), "alt_note_mapping": ALT_NOTES,
            "limits": "Original note identity and formulas checked; linguistic and pedagogical certification remain separate."}


def validate_images(document, source, translation, manifest, notices, check=require):
    figures = [n for n in source.iter() if tag(n) == "figure"]
    check("three_source_images_and_notices", len(figures) == len(manifest["images"]) == len(notices)
          == len(list(document.iter("img"))) == 3)
    check("exact_corrected_alt_keys", set(translation["image_alt_overrides"]) == set(ALT_NOTES))
    with (WORKSPACE / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv").open(encoding="utf-8-sig", newline="") as handle:
        retained = {row["asset_path"]: row for row in csv.DictReader(handle)}
    report = []
    rp = parents(document)
    for index, (figure, spec, notice) in enumerate(zip(figures, manifest["images"], notices), 7):
        media = next(n for n in figure if tag(n) == "media")
        image = next(n for n in media if tag(n) == "image")
        sid = media.get("id")
        target, actual_figure = by_id(document, sid), by_id(document, figure.get("id"))
        asset = BASE / spec["path"]
        original = WORKSPACE / "downloads/complete-upstream/osbooks-college-algebra-bundle" / spec["source_path"]
        check("image_manifest_source_identity:" + sid, figure.get("id") == spec["figure_id"] == f"Figure_01_01_{index:03}"
              and image.get("src") == "../../" + spec["source_path"] and spec["local_label"] == f"1.1.{index}")
        check("image_src_exact:" + sid, target.tag == "img" and target.get("src") == "../" + spec["path"]
              and (READER.parent / target.get("src")).resolve() == asset.resolve())
        check("asset_hash_source_copy_notice:" + sid, sha256(asset) == sha256(original) == spec["sha256"] == notice["sha256"])
        check("existing_notice_exact:" + sid, retained[spec["source_path"]] == notice
              and notice["admission"] == "admitted" and notice["source_modules"] == "m49301")
        dimensions = jpeg_dimensions(asset.read_bytes())
        check("image_dimensions_bytes:" + sid, dimensions == (spec["width"], spec["height"])
              == (int(target.get("width")), int(target.get("height")))
              and asset.stat().st_size == int(notice["bytes"]))
        check("source_alt_preserved:" + sid, target.get("data-source-alt") == translation["source_blocks"][sid + "/alt"])
        check("corrected_accessible_alt:" + sid, target.get("alt") == translation["image_alt_overrides"][sid]
              and "(1,0)" in compact(target.get("alt")) and "(0,1)" not in compact(target.get("alt")))
        check("correction_linked_accessibly:" + sid, target.get("aria-describedby") == ALT_NOTES[sid])
        wrapper = rp[target]
        check("image_wrapper_ltr:" + sid, wrapper.attrib == {"class": "figure-scroll", "dir": "ltr", "tabindex": "0",
              "role": "region", "aria-label": "اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ"})
        check("image_wrapper_pure:" + sid, len(wrapper) == 1 and wrapper[0] is target
              and wrapper.text in (None, "") and target.tail in (None, ""))
        check("image_native_width:" + sid, target.get("style") == f"--source-width:{dimensions[0]}px")
        check("image_attributes_exact:" + sid, target.attrib == {"id": sid, "src": "../" + spec["path"],
              "alt": translation["image_alt_overrides"][sid], "data-source-alt": translation["source_blocks"][sid + "/alt"],
              "aria-describedby": ALT_NOTES[sid], "width": str(dimensions[0]), "height": str(dimensions[1]),
              "style": f"--source-width:{dimensions[0]}px"})
        hint = ET.fromstring(f'<p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="../{spec["path"]}">اصل شکل وکھری کھولو</a>۔</p>')
        advisory = ET.fromstring(f'<p class="scroll-hint source-alt-advisory">ایس شکل دے ماخذ والے متبادل متن بارے <a href="#{ALT_NOTES[sid]}">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>')
        check("image_hints_exact:" + sid, len(actual_figure) == 3 and actual_figure[0] is wrapper
              and signature(actual_figure[1]) == signature(hint) and signature(actual_figure[2]) == signature(advisory))
        report.append({"figure_id": figure.get("id"), "source_path": spec["source_path"], "sha256": spec["sha256"],
                       "dimensions": dimensions, "notice_id": notice["rights_component_id"], "alt_note": ALT_NOTES[sid]})
    check("wrong_vertex_only_source_alt", "(0,1)" in compact(by_id(document, "fs-id1165137469773").get("data-source-alt")))
    return report


def validate_metadata(document, translation, manifest, check=require):
    check("document_top_level_attributes", document.attrib == {"lang": "pnb-Arab-PK", "dir": "rtl"}
          and all(document.find(path).attrib == {} for path in ("head", "body", "body/header", "body/main")))
    check("locale_unit_direction", document.get("lang") == translation["locale"] == "pnb-Arab-PK"
          and document.get("dir") == "rtl" and translation["unit"] == manifest["unit"] == "PNB-007")
    check("reader_title", text(document.find("head/title")) == translation["title"] + " — PNB-007")
    check("reader_heading", text(document.find("body/header/h1")) == translation["title"])
    check("reader_subtitle", text(document.find("body/header")[2]) == translation["subtitle"])
    check("reader_css_exact", document.find("head/style").text == (BASE / "styles/reader.css").read_text(encoding="utf-8"))
    check("body_top_level_exact", [n.tag for n in document.find("body")] == ["header", "main", "footer"])
    footer = by_id(document, "credits")
    check("credits_direction", footer.get("lang") == "en" and footer.get("dir") == "ltr")
    check("credit_scope_disclosure", all(value in text(footer) for value in ("Rice University", "OpenStax", "Jay Abramson",
          "David Lippman", "Melonie Rasmussen", "CC BY-NC-SA 4.0", "do not endorse", "Changes:",
          "1.1.7–1.1.9", "Table_01_01_12 remains unnumbered", "unit-007-component-notices.json", "not a complete textbook")))
    check("credit_original_source_url", footer.find(".//a").get("href") ==
          "https://github.com/openstax/osbooks-college-algebra-bundle/blob/" + manifest["commit"] + "/" + manifest["path"])
    check("license_and_provenance_links", {"https://creativecommons.org/licenses/by-nc-sa/4.0/",
          "../provenance/ATTRIBUTION.md"}.issubset({n.get("href") for n in footer.iter("a")}))
    check("coverage_and_review_pending", "پورے حصے دا ترجمہ نہیں" in text(document)
          and "لسانی جانچ ہن تک نہیں ہوئی" in text(document.find("body/header")))


def validate_source_directions(document, source, check=require):
    p = parents(document)
    for key, node in source_specs(source).items():
        if tag(node) in ("media", "table"):
            continue
        current = target_block(document, source, key, node)
        while current is not None and not current.get("dir"):
            current = p.get(current)
        check("source_prose_RTL:" + key, current is not None and current.get("dir") == "rtl")



def mutations(document, source, translation, manifest, notices, check):
    tested = []
    contexts = math_contexts(document, source)
    original_maths = list(source.iter("{" + MATH + "}math"))
    maths = lambda root: list(root.iter("{" + MATH + "}math"))

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

    mv = lambda d: validate_math(d, source)
    bv = lambda d: validate_blocks(d, source, translation, manifest)
    tv = lambda d: validate_tables(d, source, translation, manifest)
    iv = lambda d: validate_images(d, source, translation, manifest, notices)
    lv = lambda d: validate_links(d, source, translation, manifest)
    ov = lambda d: validate_bridge(d, source, translation)
    sv = lambda d: validate_structure(d, source)
    reject("changed_first_formula_number", lambda d: next(d.iter("{" + MATH + "}mn")).__setattr__("text", "999"), mv, "exact_math_reconstruction")

    def edit_ledger(d, context, field, value):
        target = maths(d)[contexts.index(context)]
        entries = json.loads(target.get(LEDGER))
        entries[0][field] = value
        if field == "new":
            at_path(target, entries[0]["path"]).text = value
        target.set(LEDGER, json.dumps(entries))

    reject("forged_numeric_old", lambda d: edit_ledger(d, ("fs-id1165137584852", 2), "old", "2100."), mv, "ledger_old_equals_source")
    reject("reversible_changed_numeric_value", lambda d: edit_ledger(d, ("fs-id1165137584852", 2), "new", "2100"), mv, "ledger_new_equals_policy")
    reject("reversible_changed_numeric_mtext", lambda d: edit_ledger(d, ("fs-id1165137871522/item/2", 12), "new", "4"), mv, "ledger_new_equals_policy")

    def forge_internal(d, kind, value, replacement):
        index, path = next((i, p) for i, n in enumerate(original_maths) for p, leaf in paths(n)
                           if tag(leaf) == kind and leaf.text == value and p not in permitted_edits(n, contexts[i]))
        target = maths(d)[index]
        at_path(target, path).text = replacement
        entries = json.loads(target.get(LEDGER, "[]"))
        entries.append({"path": list(path), "old": value, "new": replacement})
        target.set(LEDGER, json.dumps(entries))

    reject("reversible_internal_coordinate_comma", lambda d: forge_internal(d, "mo", ",", ""), mv, "source_position_whitelist")
    reject("reversible_English_instruction", lambda d: forge_internal(d, "mtext", "Subtract\u00a0", "Add\u00a0"), mv, "source_position_whitelist")
    reject("math_wrapper_extra_text", lambda d: parents(d)[maths(d)[0]].__setattr__("text", "999"), mv, "math_wrapper_pure")

    def duplicate_ledger(d):
        target = next(n for n in maths(d) if n.get(LEDGER))
        entries = json.loads(target.get(LEDGER))
        entries.append(copy.deepcopy(entries[0]))
        target.set(LEDGER, json.dumps(entries))

    reject("duplicate_ledger_path", duplicate_ledger, mv, "ledger_path_unique")
    reject("cube_root_degree_changed", lambda d: next(by_id(d, "fs-id1165135344102").iter("{" + MATH + "}mroot"))[1].__setattr__("text", "2"), mv, "exact_math_reconstruction")
    reject("graph_tryit_answer_changed", lambda d: next(by_id(d, "fs-id1165137598287").iter("{" + MATH + "}mn")).__setattr__("text", "1"), mv, "exact_math_reconstruction")

    def move_nested_figure(d):
        item = by_id(d, "fs-id1165137871522")[0]
        figure = by_id(d, "Figure_01_01_008")
        item.remove(figure)
        item.insert(1, figure)

    reject("nested_figure_slot_reordered", move_nested_figure, bv, "exact_fragment_and_nested_slots")
    reject("circled_part_label_changed", lambda d: by_id(d, "fs-id1165137604039")[0][0].__setattr__("text", "(b)"), sv, "part_label")
    reject("unkeyed_source_paragraph", lambda d: ET.SubElement(by_id(d, SELECTED[0]), "p", {"dir": "ltr"}).__setattr__("text", "f(2) = 999; x != 0"), sv, "complete_structural_children")
    reject("source_container_own_text", lambda d: by_id(d, SELECTED[0]).__setattr__("text", "f(2) = 999"), sv, "no_structural_text_or_tail")
    reject("source_container_child_tail", lambda d: by_id(d, SELECTED[0])[0].__setattr__("tail", "x != 0"), sv, "no_structural_text_or_tail")
    reject("source_block_extra_condition", lambda d: ET.SubElement(by_id(d, "fs-id1165137937536"), "bdi", {"dir": "ltr"}).__setattr__("text", "x != 0"), bv, "exact_fragment_and_nested_slots")
    reject("unkeyed_main_injection", lambda d: ET.SubElement(d.find("body/main"), "p").__setattr__("text", "999"), sv, "complete_main_child_sequence")
    reject("goldfish_cell_2100", lambda d: by_id(d, "Table_01_01_10").findall("./tbody/tr")[4][1].__setattr__("text", "2100"), tv, "numeric_cell_source_exact")

    def swap_rows(d):
        body = by_id(d, "Table_01_01_11")[0]
        row = body[0]
        body.remove(row)
        body.append(row)

    reject("table_row_orientation_swapped", swap_rows, tv, "numeric_cell_source_exact")

    def transpose_table(d):
        body = by_id(d, "Table_01_01_11")[0]
        columns = list(zip(*[list(row) for row in body]))
        body.clear()
        for cells in columns:
            row = ET.SubElement(body, "tr")
            row.extend(cells)

    reject("table_transposed_to_six_by_two", transpose_table, tv, "table_rows_exact")
    reject("translated_data_promoted_to_header", lambda d: by_id(d, "Table_01_01_10").findall("./tbody/tr")[1][0].__setattr__("tag", "th"), tv, "cell_semantics")
    reject("table_summary_uses_source_error", lambda d: by_id(d, "Table_01_01_10").set("aria-label", translation["source_blocks"]["Table_01_01_10/summary"]), tv, "table_attributes_exact")
    reject("invented_Table12_caption", lambda d: ET.SubElement(by_id(d, "Table_01_01_12"), "caption").__setattr__("text", "12"), tv, "table_structure_pure")
    reject("source_alt_error_silently_erased", lambda d: by_id(d, "fs-id1165137469773").set("data-source-alt", translation["image_alt_overrides"]["fs-id1165137469773"]), iv, "source_alt_preserved")
    reject("accessible_alt_wrong_vertex", lambda d: by_id(d, "fs-id1165137469773").set("alt", "راس (0,1)"), iv, "corrected_accessible_alt")
    reject("alt_note_wrong_existing_target", lambda d: by_id(d, "fs-id1165137469773").set("aria-describedby", "representations-alt-wording"), iv, "correction_linked_accessibly")
    reject("alt_visible_advisory_wrong_target", lambda d: by_id(d, "Figure_01_01_009")[2][0].set("href", "#representations-alt-wording"), iv, "image_hints_exact")
    reject("wrong_existing_image", lambda d: by_id(d, "fs-id1165137469773").set("src", "../assets/Figure_01_01_007.jpg"), iv, "image_src_exact")
    reject("wrong_image_width", lambda d: by_id(d, "fs-id1165137469773").set("width", "488"), iv, "image_dimensions_bytes")
    reject("source_link_wrong_existing_target", lambda d: by_id(d, "fs-id1165137469316").find("a").set("href", "#Figure_01_01_008"), lv, "source_link_exact")
    reject("footnote_external_URL_changed", lambda d: by_id(d, "fs-id1165135434830-text").find(".//a").set("href", "https://example.com/"), lv, "footnote_original_URL_and_date")

    def alter_date(d):
        note = by_id(d, "fs-id1165135434830-text")
        next(n for n in note.iter("bdi") if text(n) == "3/24/2014").text = "4/24/2014"

    reject("footnote_date_changed", alter_date, lv, "footnote_original_URL_and_date")
    reject("footnote_reference_wrong_target", lambda d: by_id(d, "fs-id1165135434830")[0].set("href", "#representations-bridge"), lv, "source_footnote_sup_exact")
    reject("endnote_backlink_tail_injection", lambda d: by_id(d, "fs-id1165135434830-text")[-1].__setattr__("tail", " CONTRADICTORY f(2)=999"), bv, "endnote_exact_backlink")

    def alter_original(d):
        note = by_id(d, "representations-bridge")
        next(n for n in note.iter("bdi") if compact(text(n)) == "g(3)=7").text = "g(3) = 8"

    reject("original_answer_contradicts_table", alter_original, ov, "original_fragment_exact")

    def move_original_inside_source(d):
        note = by_id(d, "representations-source-context")
        parents(d)[note].remove(note)
        by_id(d, SELECTED[0]).append(note)

    reject("original_note_relabelled_as_source_child", move_original_inside_source, ov, "original_separate_from_source")
    reject("wrong_reader_unit_metadata", lambda d: d.find("head/title").__setattr__("text", "PNB-008"), lambda d: validate_metadata(d, translation, manifest), "reader_title")
    reject("source_container_wrong_tag", lambda d: by_id(d, SELECTED[0]).__setattr__("tag", "div"), sv, "complete_main_child_sequence")
    reject("source_paragraph_direction_changed", lambda d: by_id(d, "fs-id1165137937536").set("dir", "ltr"), bv, "source_block_tag_attributes")
    reject("numeric_cell_hidden", lambda d: by_id(d, "Table_01_01_10").findall("./tbody/tr")[4][1].set("hidden", "hidden"), tv, "cell_attributes_exact")
    reject("inherited_body_direction_changed", lambda d: d.find("body").set("dir", "ltr"), lambda d: validate_source_directions(d, source), "source_prose_RTL")
    reject("math_wrapper_hidden", lambda d: parents(d)[maths(d)[0]].set("hidden", "hidden"), mv, "math_wrapper_attributes_exact")
    reject("table_wrapper_hidden", lambda d: parents(d)[by_id(d, "Table_01_01_10")].set("hidden", "hidden"), tv, "table_wrapper_attributes_exact")
    reject("image_hidden", lambda d: by_id(d, "fs-id1165137469773").set("hidden", "hidden"), iv, "image_attributes_exact")
    return tested


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", choices=["007"], default="007")
    parser.parse_args()
    manifest_path = BASE / "source-excerpts/manifest-007.json"
    translation_path = BASE / "translations/unit-007.json"
    notice_path = BASE / "provenance/unit-007-component-notices.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    translation = json.loads(translation_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    notices = json.loads(notice_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    receipts = ["PNB-007-next-unit-20260830T230304108428Z.json", "PNB-007-draft-20260830T231045082880Z.json",
                "PNB-007-revision-20260830T232155944137Z.json", "PNB-007-qa-20260830T232605954577Z.json"]
    inputs = [manifest_path, excerpt, translation_path, notice_path, BASE / "styles/reader.css",
              BASE / "terminology.tsv", BASE / "scripts/build.py", BASE / "scripts/qa_notation.py",
              BASE / "scripts/qa_evaluation.py", Path(__file__).resolve(),
              BASE / "qa/unit-007-language-notes.md", BASE / "provenance/ATTRIBUTION.md",
              *[BASE / spec["path"] for spec in manifest["images"]],
              *[BASE / "canon/receipts" / name for name in receipts]]
    initial = {p.relative_to(BASE).as_posix(): sha256(p) for p in inputs}
    command = [sys.executable, str(BASE / "scripts/build.py"), "--unit", "007"]
    subprocess.run(command, check=True)
    first = READER.read_bytes()
    subprocess.run(command, check=True)
    require("deterministic_reader_build", READER.read_bytes() == first)
    raw = first.decode("utf-8")
    document = parse_reader(raw)
    checks = ["deterministic_reader_build"]

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    check("frozen_excerpt_hash", sha256(excerpt) == manifest["excerpt_sha256"])
    for path in [*inputs, READER]:
        if path.suffix != ".jpg":
            check("unicode_clean:" + path.relative_to(BASE).as_posix(), not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", raw))
    boundary = validate_boundary(source, manifest, check)
    source_ids, pairings = validate_structure(document, source, check)
    _, numerals, totals = validate_blocks(document, source, translation, manifest, check)
    math_report = validate_math(document, source, check)
    table_report = validate_tables(document, source, translation, manifest, check)
    arithmetic_report = validate_mathematics(document, source, check)
    bridge_report = validate_bridge(document, source, translation, check)
    image_report = validate_images(document, source, translation, manifest, notices, check)
    link_report = validate_links(document, source, translation, manifest, check)
    validate_metadata(document, translation, manifest, check)
    validate_directions(document, check)
    validate_source_directions(document, source, check)
    mutation_report = mutations(document, source, translation, manifest, notices, check)
    check("mutations_leave_reader_unchanged", first == READER.read_bytes())
    final = {p.relative_to(BASE).as_posix(): sha256(p) for p in inputs}
    check("checked_inputs_stable_during_run", initial == final)
    final[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {"unit": "PNB-007", "status": "structural_pass_linguistic_visual_review_separate",
               "translated_blocks": 72, "source_ids_preserved": len(source_ids), "source_boundary": boundary,
               "exercise_pairings": pairings, "placeholder_totals": totals, "math": math_report,
               "tables": table_report, "images": image_report, "source_prose_numerals": numerals,
               "arithmetic": arithmetic_report, "original_bridge": bridge_report, "links": link_report,
               "mutation_tests": mutation_report, "check_count": len(checks), "checks": checks, "hashes": final,
               "limitations": ["Only the declared three-skill remainder is covered; no complete module/book claim.",
                               "Native-speaker, mathematics-educator and assistive-technology review remain separate.",
                               "Finite arithmetic samples are not universal proofs or verification of animal-memory science.",
                               "Raster identity/known correction contracts are checked; actual pixels/layout need visual review.",
                               "External URLs are retained, not network-tested; existing component notices are compared, not re-audited."]}
    (BASE / "qa/structural-007.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
                                              encoding="utf-8", newline="\n")
    print(f"PASS: {len(checks)} checks; 72 blocks; 84 source IDs; 83 MathML trees; 3 tables; 3 images; "
          f"{len(math_report['text_edits'])} reversible edits; {len(mutation_report)} detached mutations")


if __name__ == "__main__":
    main()
