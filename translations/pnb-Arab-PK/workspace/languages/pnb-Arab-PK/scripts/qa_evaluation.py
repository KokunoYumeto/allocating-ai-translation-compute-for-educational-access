"""Source-bound PNB-006 QA. Mutations touch detached DOMs, never manuscripts.

Only deterministic reader builds and structural-006.json are written. The four
numeric-token punctuation exceptions are source-position rules, not ledger trust.
"""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
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

from qa_notation import (MATH, LEDGER, allowed_punctuation_edits, at_path, paths,
                         signature, unique_object, jpeg_dimensions)


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
CNXML = "http://cnx.rice.edu/cnxml"
READER = BASE / "reader/unit-006.html"
SELECTED = "fs-id1165137503241"
NEXT = "fs-id1165137591827"
BLOCKS = {"figure", "para", "note", "list", "exercise", "problem", "solution",
          "section", "equation", "example", "table", "footnote"}
MN_EXCEPTIONS = {
    ("fs-id1165137460826", 1): "3.",
    ("fs-id1165134468906", 2): "3.",
    ("fs-id1165134468906", 4): "24.",
    ("fs-id1165134170174", 1): "2.",
}
FORBIDDEN = re.compile(r"[\u0a00-\u0a7f\ufffd\u061c\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def text(node):
    return "".join(node.itertext()).strip()


def compact(value):
    return re.sub(r"\s+", "", value)


def sha256(path, normalize_xml=True):
    data = path.read_bytes()
    if normalize_xml and path.suffix == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def parse_reader(raw):
    return ET.fromstring(raw[raw.index("<html"):])


def parents(document):
    return {child: parent for parent in document.iter() for child in parent}


def by_id(document, identifier):
    matches = [node for node in document.iter() if node.get("id") == identifier]
    require("unique_id:" + identifier, len(matches) == 1)
    return matches[0]


def own_math(node):
    result = []
    for child in node:
        if tag(child) == "math":
            result.append(child)
        elif tag(child) not in BLOCKS:
            result.extend(own_math(child))
    return result


def own_source_text(node):
    result = node.text or ""
    for child in node:
        if tag(child) not in BLOCKS | {"math", "link"}:
            result += own_source_text(child)
        result += child.tail or ""
    return result


def source_specs(source):
    result = {}

    def visit(node, parent=None, index=0):
        name = tag(node)
        if name == "equation":
            return
        if name == "media":
            result[node.get("id") + "/alt"] = node
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


def target_block(document, source, node):
    if node.get("id"):
        return by_id(document, node.get("id"))
    parent = parents(source)[node]
    rendered_parent = by_id(document, parent.get("id"))
    if tag(node) == "item":
        return rendered_parent.findall("li")[list(parent).index(node)]
    heading = "h2" if tag(node) == "title" and tag(parent) == "section" else "h3"
    matches = rendered_parent.findall(heading)
    require("one_source_heading:" + parent.get("id"), len(matches) == 1)
    return matches[0]


def validate_boundary(source, manifest, check=require):
    witnesses = manifest["source_byte_witnesses"]
    pinned = WORKSPACE / witnesses["pinned_lf_witness_path"]
    checkout = WORKSPACE / witnesses["canonical_checkout_path"]
    check("pinned_module_hash", sha256(pinned, False) == manifest["full_module_sha256"])
    check("raw_checkout_hash", sha256(checkout, False) == witnesses["canonical_checkout_sha256"])
    check("checkout_only_crlf_differs", checkout.read_bytes().replace(b"\r\n", b"\n") == pinned.read_bytes())
    comparison = WORKSPACE / witnesses["comparison_path"]
    check("comparison_hash", sha256(comparison, False) == witnesses["comparison_sha256"])
    full = ET.parse(pinned).getroot()
    original = by_id(full, SELECTED)
    prefix = copy.deepcopy(original)
    for child in list(prefix)[4:]:
        prefix.remove(child)
    check("exact_source_prefix_including_whitespace", len(source) == 1 and signature(prefix) == signature(source[0]))
    check("exact_selected_wrapper_and_next_child", manifest["selection_ids"] == [SELECTED]
          and manifest["next_source_id"] == NEXT == list(original)[4].get("id"))
    boundary = manifest["selection_boundary"]
    check("first_four_direct_children", len(prefix) == 4 and [tag(n) for n in prefix] == ["title", "para", "para", "section"]
          and [n.get("id") for n in list(prefix)[1:]] == ["fs-id1165137470651", "fs-id1165137735634", "fs-id1165137425943"]
          and boundary["outer_section_id"] == SELECTED and boundary["next_direct_child_id"] == NEXT)
    expected_children = [{"index": 1, "tag": "title", "source_key": SELECTED + "/title"},
                         {"index": 2, "tag": "para", "id": "fs-id1165137470651"},
                         {"index": 3, "tag": "para", "id": "fs-id1165137735634"},
                         {"index": 4, "tag": "section", "id": "fs-id1165137425943", "coverage": "complete subtree"}]
    check("manifest_explicit_prefix_not_whole_section", boundary["included_direct_children"] == expected_children)
    identifiers = [n.get("id") for n in prefix.iter() if n.get("id")]
    check("last_selected_source_id", identifiers[-1] == boundary["last_selected_descendant_id"] == "fs-id1165135664056")
    parent = parents(full)[original]
    following = list(parent)[list(parent).index(original) + 1]
    check("whole_outer_section_following_cursor_distinct", following.get("id")
          == boundary["following_complete_outer_section_id"] == "fs-id1165135422920")
    return {"selected": SELECTED, "children": expected_children, "next_source_id": NEXT,
            "last_source_id": identifiers[-1], "whole_section_following": following.get("id")}


def validate_structure(document, source, check=require):
    ids = [n.get("id") for n in document.iter() if n.get("id")]
    originals = [n for n in source.iter() if n is not source and n.get("id")]
    source_ids = [n.get("id") for n in originals]
    check("unique_reader_ids", len(ids) == len(set(ids)))
    check("all_55_source_ids_exact_order", len(source_ids) == 55 and [i for i in ids if i in source_ids] == source_ids)
    check("excerpt_wrapper_not_rendered", source.get("id") not in ids)
    source_parent, target_parent = parents(source), parents(document)

    def chain(node, parent):
        result = []
        while node in parent:
            node = parent[node]
            if node.get("id") in source_ids:
                result.append(node.get("id"))
        return result

    check("all_source_id_ancestor_chains", all(chain(n, source_parent) == chain(by_id(document, n.get("id")), target_parent)
          for n in originals))
    # IDs alone cannot reject an unkeyed paragraph, anonymous heading, or text
    # injected between source blocks. Bind every structural container's complete
    # child sequence, not merely the subsequence of identified descendants.
    structural = {"section", "example", "exercise", "problem", "solution", "commentary", "note", "list", "figure"}
    output_tags = {"section": "section", "example": "section", "exercise": "div", "problem": "div",
                   "solution": "section", "commentary": "div", "note": "aside", "list": "ol",
                   "figure": "figure", "para": "p", "item": "li", "equation": "div", "label": "h3"}
    for original in (n for n in source.iter() if tag(n) in structural):
        rendered = by_id(document, original.get("id"))
        expected = []
        if tag(original) == "example":
            expected.append(("h2", None))
            number = int(original.get("id").rsplit("_", 1)[-1])
            heading = ET.fromstring(f'<h2>حل کیتی مثال <bdi dir="ltr">{number}</bdi></h2>')
            check("automatic_example_heading_exact:" + original.get("id"), signature(rendered[0]) == signature(heading))
        elif tag(original) == "solution":
            expected.append(("h3", None))
            check("automatic_solution_heading_exact:" + original.get("id"), signature(rendered[0]) == signature(ET.fromstring('<h3>حل</h3>')))
        for child in original:
            name = tag(child)
            if name == "media":
                expected.extend([("div", None), ("p", None)])
            else:
                output = ("h2" if tag(original) == "section" else "h3") if name == "title" else output_tags[name]
                expected.append((output, child.get("id")))
        check("complete_structural_children:" + original.get("id"), [(n.tag, n.get("id")) for n in rendered] == expected)
        check("no_structural_text_injection:" + original.get("id"), rendered.text in (None, "")
              and all(n.tail in (None, "") for n in rendered))
        check("source_container_has_no_omitted_own_prose:" + original.get("id"), not (original.text or "").strip()
              and all(not (n.tail or "").strip() for n in original))
    examples = [n for n in source.iter() if tag(n) == "example"]
    check("examples_06_07_08", [n.get("id") for n in examples] == ["Example_01_01_06", "Example_01_01_07", "Example_01_01_08"])
    for number, original in enumerate(examples, 6):
        rendered = by_id(document, original.get("id"))
        check("example_number:" + original.get("id"), rendered.tag == "section" and rendered.get("class") == "source-example"
              and rendered.find("h2/bdi") is not None and text(rendered.find("h2/bdi")) == str(number))
    pairings = []
    for exercise in (n for n in source.iter() if tag(n) == "exercise"):
        expected = [(tag(n), n.get("id")) for n in exercise]
        rendered = by_id(document, exercise.get("id"))
        check("exercise_problem_solution_pairing:" + exercise.get("id"),
              [(n.get("class", "").removeprefix("source-"), n.get("id")) for n in rendered] == expected
              and [kind for kind, _ in expected] == ["problem", "solution"])
        pairings.append({"exercise": exercise.get("id"), "problem": expected[0][1], "solution": expected[1][1]})
    check("five_complete_exercises", len(pairings) == 5)
    for list_id, count in [("fs-id1165137629040", 2), ("fs-id1165137648008", 4), ("fs-id1165137778273", 4)]:
        rendered = by_id(document, list_id)
        check("ordered_list:" + list_id, rendered.tag == "ol" and len(rendered.findall("li")) == count)
        if count == 4:
            check("circled_parts_accessible_list:" + list_id, rendered.get("role") == "list" and rendered.get("class") == "source-parts")
            for index, item in enumerate(rendered.findall("li")):
                check(f"part_label:{list_id}:{index}", len(item) > 0 and item[0].tag == "bdi"
                      and item[0].get("dir") == "ltr" and text(item[0]) == f"({chr(97 + index)})")
    return source_ids, pairings


def content_signature(node):
    return node.text, tuple((signature(child), child.tail) for child in node)


def validate_blocks(document, source, translation, manifest, check=require):
    specs = source_specs(source)
    blocks = translation["source_blocks"]
    check("all_37_keys_exact_in_order", len(specs) == len(blocks) == 37 and list(specs) == list(blocks))
    labels = {spec["figure_id"]: spec["local_label"] for spec in manifest["images"]}
    totals = {"math": 0, "link": 0, "child": 0}
    numerals = {}
    for key, original in specs.items():
        rendered = target_block(document, source, original)
        value = blocks[key]
        if tag(original) == "media":
            check("source_alt_exact:" + key, rendered.tag == "img" and rendered.get("alt") == value)
            original_prose, visible = original.get("alt"), value
        else:
            maths, links = own_math(original), [n for n in original if tag(n) == "link"]
            children = [n for n in original if tag(n) in BLOCKS]
            for kind, nodes in (("math", maths), ("link", links), ("child", children)):
                check(f"ordered_{kind}_placeholders:{key}", [int(i) for i in re.findall(r"\{\{" + kind + r":(\d+)\}\}", value)] == list(range(len(nodes))))
                totals[kind] += len(nodes)
            child_ids = [n.get("id") for n in children]
            check("exact_immediate_block_children:" + key, [n.get("id") for n in rendered if n.get("id")] == child_ids)
            expected = re.sub(r"\{\{(math|child):(\d+)\}\}", r'<slot kind="\1" index="\2" />', value)
            expected = re.sub(r"\{\{link:(\d+)\}\}", lambda m: '<a href="#' + links[int(m[1])].get("target-id")
                              + '">شکل <bdi dir="ltr">' + labels[links[int(m[1])].get("target-id")] + '</bdi></a>', expected)
            expected = ET.fromstring("<fragment>" + expected + "</fragment>")
            actual = copy.deepcopy(rendered)
            counter = [0]

            def slots(node):
                for index, child in enumerate(list(node)):
                    replacement = None
                    if child.get("id") in child_ids:
                        replacement = ET.Element("slot", {"kind": "child", "index": str(child_ids.index(child.get("id")))})
                    elif child.get("class") == "math-isolate":
                        replacement = ET.Element("slot", {"kind": "math", "index": str(counter[0])})
                        counter[0] += 1
                    else:
                        slots(child)
                    if replacement is not None:
                        replacement.tail = child.tail
                        node.remove(child)
                        node.insert(index, replacement)

            slots(actual)
            check("exact_translated_fragment_and_slot_positions:" + key, content_signature(actual) == content_signature(expected))
            check("own_rendered_math_slots:" + key, counter[0] == len(maths))
            clean = ET.fromstring("<fragment>" + re.sub(r"\{\{(?:math|link|child):\d+\}\}", "", value) + "</fragment>")
            original_prose, visible = own_source_text(original), text(clean)
            expected_emphasis = ["em" if n.get("effect") == "italics" else "strong" for n in original if tag(n) == "emphasis"]
            check("source_emphasis_retained:" + key, [n.tag for n in rendered if n.tag in ("em", "strong")] == expected_emphasis)
        digits = re.findall(r"\d+(?:\.\d+)?", original_prose)
        check("source_prose_numbers:" + key, re.findall(r"\d+(?:\.\d+)?", visible) == digits)
        if digits:
            numerals[key] = digits
    check("29_inline_math_one_link_eight_children", totals == {"math": 29, "link": 1, "child": 8})
    check("part_d_five_child_sequence", [n.get("id") for n in specs["fs-id1165137778273/item/4"] if tag(n) in BLOCKS]
          == ["fs-id1165135154122", "fs-id1165135632109", "fs-id1165137471110", "fs-id1165137767461", "fs-id1165137573884"])
    return specs, numerals, totals


def permitted_edits(original, context):
    """Independent source owner/slot plus terminal-position MN whitelist."""
    allowed = allowed_punctuation_edits(original)
    if context in MN_EXCEPTIONS:
        leaves = [(path, node) for path, node in paths(original) if not len(node)]
        path, leaf = leaves[-1]
        expected = MN_EXCEPTIONS[context]
        require("mn_source_exception_position:" + str(context), tag(leaf) == "mn"
                and leaf.text == expected and re.fullmatch(r"[0-9]+\.", leaf.text) is not None)
        new = expected[:-1]
        require("mn_exception_numeric_semantics:" + str(context), Decimal(expected) == Decimal(new))
        allowed[path] = (expected, new)
    return allowed


def restore_math(original, rendered, context):
    require("math_root_ltr:" + str(context), rendered.get("dir") == "ltr")
    require("source_no_presentation_metadata", "dir" not in original.attrib and LEDGER not in original.attrib)
    raw = rendered.get(LEDGER)
    try:
        entries = [] if raw is None else json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise AssertionError("ledger_valid_json") from error
    require("ledger_list_nonempty_when_present", isinstance(entries, list) and (raw is None or bool(entries)))
    allowed = permitted_edits(original, context)
    restored, seen = copy.deepcopy(rendered), set()
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


def validate_math(document, source, check=require):
    originals = list(source.iter("{" + MATH + "}math"))
    rendered = [n for n in document.iter() if tag(n) == "math"]
    check("all_38_math_trees_exact_namespace", len(originals) == len(rendered) == 38
          and all(n.tag == "{" + MATH + "}math" for n in rendered))
    specs = source_specs(source)
    owner_source = {n: key for key, n in specs.items()}
    owner_target = {target_block(document, source, n): key for key, n in specs.items()}
    equations = [n for n in source.iter() if tag(n) == "equation"]
    for equation in equations:
        owner_source[equation] = equation.get("id")
        owner_target[by_id(document, equation.get("id"))] = equation.get("id")

    def owners(nodes, parent, mapping):
        result, counts = [], {}
        for node in nodes:
            while node in parent:
                node = parent[node]
                if node in mapping:
                    key = mapping[node]
                    slot = counts.get(key, 0)
                    result.append((key, slot))
                    counts[key] = slot + 1
                    break
            else:
                raise AssertionError("math_has_source_owner")
        return result

    op, rp = parents(source), parents(document)
    contexts = owners(originals, op, owner_source)
    check("all_math_owners_and_per_owner_slots_exact", contexts == owners(rendered, rp, owner_target))
    edits, english, mn_entries = [], [], []
    for index, (original, target, context) in enumerate(zip(originals, rendered, contexts)):
        wrapper = rp[target]
        check(f"math_wrapper_ltr:{index}", wrapper.tag == "span" and wrapper.get("class") == "math-isolate" and wrapper.get("dir") == "ltr")
        check(f"math_wrapper_pure:{index}", len(wrapper) == 1 and wrapper[0] is target
              and wrapper.text in (None, "") and target.tail in (None, ""))
        entries = restore_math(original, target, context)
        check(f"math_exact_reversible_tree:{index}", True)
        edits.extend({"tree": index, "owner": context[0], "slot": context[1], **entry} for entry in entries)
        if context in MN_EXCEPTIONS:
            mn_entries.extend(entries)
        for path, leaf in paths(original):
            if tag(leaf) == "mtext" and re.search("[A-Za-z]", leaf.text or ""):
                check(f"english_mtext_and_nbsp_exact:{index}:{path}", at_path(target, path).text == leaf.text)
                english.append(leaf.text)
    check("nine_display_equations", len(equations) == 9 and sum(n.get("display") == "block" for n in rendered) == 9)
    for original in equations:
        target = by_id(document, original.get("id"))
        check("display_container_pure:" + original.get("id"), target.tag == "div" and target.get("dir") == "ltr"
              and target.text in (None, "") and len(target) == 1 and target[0].get("class") == "math-isolate"
              and target[0].tail in (None, "") and target[0].get("role") == "region" and target[0].get("tabindex") == "0")
    check("ledgers_only_on_math_roots", all(n in rendered for n in document.iter() if LEDGER in n.attrib))
    check("four_independent_terminal_mn_exceptions", len(mn_entries) == 4 and set(MN_EXCEPTIONS).issubset(contexts))
    check("fifteen_source_derived_edge_edits", len(edits) == 15)
    return {"trees": 38, "inline_trees": 29, "equations": 9, "text_edits": edits,
            "mn_exception_count": len(mn_entries), "source_contexts": contexts, "english_mtext": english}


def math_string(node):
    """Compact formula reading; exact trees are checked separately, not flattened."""
    name = tag(node)
    if name == "msup":
        return math_string(node[0]) + ("²" if text(node[1]) == "2" else "^(" + math_string(node[1]) + ")")
    if name == "msqrt":
        return "√(" + "".join(math_string(n) for n in node) + ")"
    return (node.text or "") + "".join(math_string(n) + (n.tail or "") for n in node)


def arithmetic(node, values):
    name = tag(node)
    if name == "mn":
        return float(node.text.rstrip(".,:"))
    if name == "mi":
        return values[node.text]
    if name == "msup":
        return arithmetic(node[0], values) ** arithmetic(node[1], values)
    if name == "msqrt":
        return math.sqrt(arithmetic_sequence(list(node), values))
    if name == "mfrac":
        return arithmetic(node[0], values) / arithmetic(node[1], values)
    require("supported_arithmetic_node", name in ("mrow", "math"))
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
    require("arithmetic_expression_numeric_only", re.fullmatch(r"[0-9eE+*/(). -]+", expression) is not None)
    return eval(expression, {"__builtins__": {}}, {})


def rhs(math_node):
    nodes = list(math_node[0])
    position = next(i for i, n in enumerate(nodes) if tag(n) == "mo" and n.text == "=")
    return nodes[position + 1:]


def validate_mathematics(document, source, check=require):
    def formula(root, identifier):
        return next(by_id(root, identifier).iter("{" + MATH + "}math"))

    fs = formula(source, "fs-id1165134193005")
    hs = formula(source, "fs-id1165137731385")
    gs = formula(source, "fs-id1165134039323")
    ft = formula(document, "fs-id1165134193005")
    ht = formula(document, "fs-id1165137731385")
    gt = formula(document, "fs-id1165134039323")
    f = lambda x: arithmetic_sequence(rhs(ft), {"x": x})
    h = lambda p: arithmetic_sequence(rhs(ht), {"p": p})
    g = lambda m: arithmetic_sequence(rhs(gt), {"m": m})
    for x in (-3, -1, 0, 1, 2, 4, 5):
        check(f"rendered_f_matches_source_evaluation:{x}", f(x) == arithmetic_sequence(rhs(fs), {"x": x}))
        check(f"rendered_h_matches_source_evaluation:{x}", h(x) == arithmetic_sequence(rhs(hs), {"p": x}))
    for m in (4, 5, 8, 13):
        check(f"rendered_g_matches_source_evaluation:{m}", g(m) == arithmetic_sequence(rhs(gs), {"m": m}))
    check("worked_numeric_answers", f(2) == 6 and h(4) == 24 and h(-3) == h(1) == 3)
    check("square_root_try_it_answers", g(5) == 1 and g(8) == 2)
    check("try_it_answers_displayed_exactly", compact(math_string(formula(document, "fs-id1165134037488"))) == "g(5)=1"
          and compact(math_string(formula(document, "fs-id1165135664056"))) == "m=8")
    try:
        g(3)
        rejected = False
    except ValueError:
        rejected = True
    check("real_square_root_domain_rejects_negative_radicand", rejected)
    tested = []
    for a in (-3, -1, 0, 2, 5):
        for increment in (-2, -1, 1, 3):
            check(f"nonzero_h_difference_quotient_sample:{a}:{increment}",
                  abs((f(a + increment) - f(a)) / increment - (2 * a + increment + 3)) < 1e-9)
            tested.append([a, increment])
    return {"numeric_answers": {"f(2)": f(2), "h(4)": h(4), "h(-3)": h(-3), "h(1)": h(1), "g(5)": g(5), "g(8)": g(8)},
            "nonzero_h_samples": tested, "claim": "Bounded arithmetic checks, not a universal proof; exact source derivations are separately reconstructed."}


def validate_bridge(document, source, translation, check=require):
    bridge, selected = by_id(document, "evaluation-bridge"), by_id(document, SELECTED)
    p = parents(document)
    check("original_bridge_separate_from_source", bridge.get("data-origin") == "original-bridge"
          and bridge not in set(selected.iter()) and p[bridge] is p[selected])
    check("h_nonzero_condition_only_in_original_support", "h≠0" in compact(text(bridge))
          and "h≠0" not in compact(text(selected)) and "≠" not in text(source))
    check("bridge_exact_saved_original_fragment", signature(bridge) == signature(ET.fromstring(translation["bridge_after_html"])))
    require("no_original_bridge_inside_source", not any(n.get("data-origin") == "original-bridge" for n in selected.iter()))
    bdis = {compact(text(n)) for n in bridge.iter("bdi")}
    source_forms = [("fs-id1165137655584", "f(x)=5−3x²"), ("fs-id1165134193005", "f(x)=x²+3x−4"),
                    ("fs-id1165134039323", "g(m)=√(m−4)")]
    for identifier, expected in source_forms:
        math_node = own_math(by_id(source, identifier))[0]
        check("local_function_definition_key:" + identifier, compact(math_string(math_node)).rstrip(".,") == expected and expected in bdis)
    for expected in ("h(4)=24", "h(p)=3", "p=−3", "p=1", "g(5)=1", "g(m)=2", "m=8", "m≥4",
                     "(f(a+h)−f(a))/h=2a+h+3", "(a+h)²=a²+2ah+h²", "3(a+h)=3a+3h"):
        check("precision_or_derived_formula_present:" + expected, expected in bdis)
    english = {re.sub(r"\s+", " ", text(n)) for n in bridge.iter("bdi") if n.get("lang") == "en"}
    required = {"Factor out h.", "Simplify.", "Substitute the original function", "Subtract 3 from each side.", "Factor."}
    check("all_mtable_instruction_keys_present", required.issubset(english))
    source_words = [re.sub(r"\s+", " ", n.text).strip() for n in source.iter("{" + MATH + "}mtext") if re.search(r"[A-Za-z]", n.text or "")]
    check("instruction_keys_bound_to_source_mtext", set(source_words) == {"Factor out", "Simplify", "Substitute the original function", "Subtract 3 from each side", "Factor"})
    for item in bridge.findall("./ul/li"):
        check("bilingual_key_has_punjabi:" + text(item.find("bdi")), re.search(r"[\u0600-\u06ff]", text(item)) is not None)
    pairs = [(int(x), int(y)) for x, y in re.findall(r"\(([−-]?\d+),\s*(\d+)\)", text(bridge).replace("−", "-"))]
    alt = next(n for n in source.iter() if tag(n) == "media").get("alt")
    expected_pairs = [(int(x), int(y)) for x, y in re.findall(r"\((-?\d+),\s*(\d+)\)", alt)]
    check("graph_original_key_points_match_source_alt", pairs == expected_pairs == [(-3, 3), (1, 3), (4, 24)])
    return {"english_key": sorted(english), "source_mtext": source_words, "graph_pairs": pairs,
            "precision_condition": "h != 0 only in original bridge"}


def validate_image(document, source, manifest, notices, check=require):
    figures = [n for n in source.iter() if tag(n) == "figure"]
    check("single_image_and_notice", len(figures) == len(manifest["images"]) == len(notices) == len(list(document.iter("img"))) == 1)
    figure, spec, notice = figures[0], manifest["images"][0], notices[0]
    media = next(n for n in figure if tag(n) == "media")
    image = next(n for n in media if tag(n) == "image")
    target = by_id(document, media.get("id"))
    check("figure_media_and_local_label", figure.get("id") == spec["figure_id"] == "Figure_01_01_006"
          and media.get("id") == "fs-id1165135335985" and spec["local_label"] == "1.1.6"
          and target in set(by_id(document, figure.get("id")).iter()))
    asset = BASE / spec["path"]
    original = WORKSPACE / "downloads/complete-upstream/osbooks-college-algebra-bundle" / spec["source_path"]
    check("image_src_exact_source_binding", target.tag == "img" and target.get("src") == "../" + spec["path"]
          and (READER.parent / target.get("src")).resolve() == asset.resolve()
          and PurePosixPath(image.get("src")).name == PurePosixPath(spec["source_path"]).name)
    check("image_hash_source_copy_manifest_notice", sha256(asset) == sha256(original) == spec["sha256"] == notice["sha256"])
    dimensions = jpeg_dimensions(asset.read_bytes())
    check("image_dimensions_and_bytes", dimensions == (487, 459) == (spec["width"], spec["height"])
          == (int(target.get("width")), int(target.get("height"))) and asset.stat().st_size == int(notice["bytes"]))
    check("image_native_width_style", target.get("style") == "--source-width:487px")
    wrapper = parents(document)[target]
    check("image_ltr_focusable_scroll", wrapper.get("class") == "figure-scroll" and wrapper.get("dir") == "ltr"
          and wrapper.get("tabindex") == "0" and wrapper.get("role") == "region")
    check("image_wrapper_contains_only_image", len(wrapper) == 1 and wrapper[0] is target
          and wrapper.text in (None, "") and target.tail in (None, ""))
    rendered_figure = by_id(document, figure.get("id"))
    hint = ET.fromstring('<p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="../'
                        + spec["path"] + '">اصل شکل وکھری کھولو</a>۔</p>')
    check("generated_image_hint_exact", len(rendered_figure) == 2 and signature(rendered_figure[1]) == signature(hint))
    rights = WORKSPACE / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv"
    with rights.open(encoding="utf-8-sig", newline="") as handle:
        retained = [row for row in csv.DictReader(handle) if row["asset_path"] == spec["source_path"]]
    check("notice_is_exact_existing_component_row", retained == notices and notice["asset_path"] == spec["source_path"]
          and notice["source_modules"] == "m49301" and notice["admission"] == "admitted")
    footer = text(by_id(document, "credits"))
    check("figure_credit_change_notice_nonendorsement", all(value in footer for value in
          ("Figure_01_01_006", "1.1.6", "Rice University", "CC BY-NC-SA 4.0", "do not endorse", "Changes:")))
    return {"source_id": figure.get("id"), "path": spec["path"], "sha256": sha256(asset), "width": dimensions[0],
            "height": dimensions[1], "retained_notice_id": notice["rights_component_id"]}


def validate_links(document, source, manifest, check=require):
    original = by_id(source, "fs-id1165134468906")
    links = [n for n in original if tag(n) == "link"]
    actual = by_id(document, original.get("id")).findall("a")
    check("one_source_link_exact_target", len(links) == len(actual) == 1 and actual[0].get("href") == "#" + links[0].get("target-id") == "#Figure_01_01_006")
    check("source_link_ltr_local_label", len(actual[0]) == 1 and actual[0][0].tag == "bdi"
          and actual[0][0].get("dir") == "ltr" and text(actual[0][0]) == manifest["images"][0]["local_label"] and actual[0].text == "شکل ")
    check("one_source_link_no_footnote_or_table", len(list(source.iter("{" + CNXML + "}link"))) == 1
          and not any(tag(n) in ("footnote", "table") for n in source.iter()))
    local = []
    for node in document.iter():
        for attribute in ("href", "src"):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
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
    check("previous_unit_navigation", any(n.get("href") == "unit-005.html" for n in document.findall(".//nav/a")))
    return local


def validate_directions(document, check=require):
    p = parents(document)

    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = p.get(node)
        return None

    check("all_bdi_ltr", all(n.get("dir") == "ltr" for n in document.iter("bdi")))
    check("english_lanes_ltr", all(direction(n) == "ltr" for n in document.iter() if n.get("lang") == "en"))
    check("all_visible_latin_digits_ltr", all(direction(n) == "ltr" for n in document.find("body").iter()
          for value in [n.text or "", *[c.tail or "" for c in n]] if re.search("[A-Za-z0-9]", value)))


def mutations(document, source, translation, manifest, notices, check):
    tested = []

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

    maths = lambda d: list(d.iter("{" + MATH + "}math"))
    math_validator = lambda d: validate_math(d, source)
    reject("changed_math_number", lambda d: next(d.iter("{" + MATH + "}mn")).__setattr__("text", "999"), math_validator, "exact_math_reconstruction")

    def mn_ledger(d, field, value):
        node = maths(d)[23]
        entries = json.loads(node.get(LEDGER))
        entries[0][field] = value
        if field == "new":
            at_path(node, entries[0]["path"]).text = value
        node.set(LEDGER, json.dumps(entries))

    reject("forged_mn_old", lambda d: mn_ledger(d, "old", "30."), math_validator, "ledger_old_equals_source")
    reject("mn_numeric_change_even_with_reversible_ledger", lambda d: mn_ledger(d, "new", "30"), math_validator, "ledger_new_equals_policy")

    def forge_internal(d, kind, before, after):
        source_maths = list(source.iter("{" + MATH + "}math"))
        index, path = next((i, p) for i, node in enumerate(source_maths) for p, leaf in paths(node)
                           if tag(leaf) == kind and leaf.text == before and p not in allowed_punctuation_edits(node))
        target = maths(d)[index]
        at_path(target, path).text = after
        entries = json.loads(target.get(LEDGER, "[]"))
        entries.append({"path": list(path), "old": before, "new": after})
        target.set(LEDGER, json.dumps(entries))

    reject("reversible_internal_numeric_edit", lambda d: forge_internal(d, "mn", "5", "6"), math_validator, "source_position_whitelist")
    reject("reversible_combined_parentheses_edit", lambda d: forge_internal(d, "mtext", ")(", "("), math_validator, "source_position_whitelist")
    reject("reversible_english_instruction_edit", lambda d: forge_internal(d, "mtext", "Simplify", "Cancel"), math_validator, "source_position_whitelist")
    reject("extra_math_wrapper_text", lambda d: parents(d)[maths(d)[0]].__setattr__("text", "999"), math_validator, "math_wrapper_pure:")

    def swap_children(d):
        item = by_id(d, "fs-id1165137778273").findall("li")[3]
        left, right = list(item)[1:3]
        item.remove(left)
        item.remove(right)
        item.insert(1, right)
        item.insert(2, left)

    reject("nested_part_d_child_order", swap_children,
           lambda d: validate_blocks(d, source, translation, manifest), "exact_immediate_block_children:")
    reject("changed_try_it_answer", lambda d: list(by_id(d, "fs-id1165135664056").iter("{" + MATH + "}mn"))[0].__setattr__("text", "9"),
           math_validator, "exact_math_reconstruction")
    reject("wrong_image_identity", lambda d: by_id(d, "fs-id1165135335985").set("src", "../assets/Figure_01_01_001.jpg"),
           lambda d: validate_image(d, source, manifest, notices), "image_src_exact_source_binding")
    reject("wrong_existing_source_link", lambda d: by_id(d, "fs-id1165134468906").find("a").set("href", "#Example_01_01_06"),
           lambda d: validate_links(d, source, manifest), "one_source_link_exact_target")
    reject("lost_original_h_nonzero_condition", lambda d: next(n for n in by_id(d, "evaluation-bridge").iter("bdi") if compact(text(n)) == "h≠0").__setattr__("text", "h = 0"),
           lambda d: validate_bridge(d, source, translation), "h_nonzero_condition_only_in_original_support")

    def source_injection(d):
        added = ET.SubElement(by_id(d, "fs-id1165137936905"), "bdi", {"dir": "ltr"})
        added.text = "h ≠ 0"

    reject("original_condition_injected_into_source", source_injection,
           lambda d: validate_bridge(d, source, translation), "h_nonzero_condition_only_in_original_support")

    def unkeyed_paragraph(d):
        added = ET.SubElement(by_id(d, SELECTED), "p", {"dir": "ltr"})
        added.text = "f(2) = 999; h != 0"

    reject("unkeyed_source_paragraph_with_contradictory_answer", unkeyed_paragraph,
           lambda d: validate_structure(d, source), "complete_structural_children:")
    return tested


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", choices=["006"], default="006")
    parser.parse_args()
    manifest_path = BASE / "source-excerpts/manifest-006.json"
    translation_path = BASE / "translations/unit-006.json"
    notice_path = BASE / "provenance/unit-006-component-notices.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    translation = json.loads(translation_path.read_text(encoding="utf-8"))
    notices = json.loads(notice_path.read_text(encoding="utf-8"))
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    inputs = [manifest_path, excerpt, translation_path, notice_path, BASE / "styles/reader.css",
              BASE / "terminology.tsv", BASE / "scripts/build.py", BASE / "scripts/qa_notation.py",
              Path(__file__).resolve(), BASE / "qa/unit-006-language-notes.md", BASE / "provenance/ATTRIBUTION.md",
              *[BASE / spec["path"] for spec in manifest["images"]]]
    initial = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    command = [sys.executable, str(BASE / "scripts/build.py"), "--unit", "006"]
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

    check("locale_unit_direction", document.get("lang") == translation["locale"] == "pnb-Arab-PK"
          and document.get("dir") == "rtl" and translation["unit"] == manifest["unit"] == "PNB-006")
    check("frozen_excerpt_hash", sha256(excerpt) == manifest["excerpt_sha256"])
    for path in [*inputs, READER]:
        if path.suffix != ".jpg":
            check("unicode_clean:" + path.relative_to(BASE).as_posix(), not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", raw))
    boundary = validate_boundary(source, manifest, check)
    source_ids, pairings = validate_structure(document, source, check)
    _, numerals, totals = validate_blocks(document, source, translation, manifest, check)
    math_report = validate_math(document, source, check)
    arithmetic_report = validate_mathematics(document, source, check)
    bridge_report = validate_bridge(document, source, translation, check)
    image_report = validate_image(document, source, manifest, notices, check)
    local = validate_links(document, source, manifest, check)
    validate_directions(document, check)
    check("bounded_coverage_disclosure", "پورے حصے دا ترجمہ نہیں" in raw)
    mutation_report = mutations(document, source, translation, manifest, notices, check)
    check("mutations_leave_reader_unchanged", first == READER.read_bytes())
    final = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    check("all_checked_inputs_stable_during_run", initial == final)
    final[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {"unit": "PNB-006", "status": "structural_pass_linguistic_and_visual_review_separate",
               "translated_blocks": len(translation["source_blocks"]), "source_ids_preserved": len(source_ids),
               "source_boundary": boundary, "exercise_pairings": pairings, "placeholder_totals": totals,
               "math": math_report, "source_prose_numerals": numerals, "arithmetic": arithmetic_report,
               "original_bridge": bridge_report, "image": image_report, "local_references": local,
               "mutation_tests": mutation_report, "check_count": len(checks), "checks": checks, "hashes": final,
               "limitations": ["Only the declared prefix is covered; the five-work assignment remains active.",
                               "Native-speaker and educator approval remain pending; exact text does not prove idiomaticity.",
                               "Finite arithmetic tests are not a universal proof; exact symbolic source trees are independently preserved.",
                               "Bilingual-key presence and source separation are checked, not certified pedagogical wording.",
                               "Raster identity is checked; visual shaping, image semantics, narrow-screen layout and assistive technology need separate review.",
                               "External URLs are retained but not network-tested; existing component records are compared, not re-audited."]}
    (BASE / "qa/structural-006.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(checks)} checks; 37 blocks; 55 source IDs; 38 MathML trees; {len(math_report['text_edits'])} reversible edits; {len(mutation_report)} detached mutations")


if __name__ == "__main__":
    main()
