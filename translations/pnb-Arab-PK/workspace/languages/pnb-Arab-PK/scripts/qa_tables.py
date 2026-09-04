"""Source-bound PNB-005 QA; only builds and a deterministic receipt are written.

All adversarial tests use detached DOMs. Numeric sign normalization is confined
to in-memory arithmetic; source cells, summaries and MathML stay byte-faithful.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import copy
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from qa_notation import (MATH, LEDGER, allowed_punctuation_edits, at_path,
                         paths, restore_math, signature)


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
READER = BASE / "reader/unit-005.html"
MANIFEST = BASE / "source-excerpts/manifest-005.json"
TRANSLATION = BASE / "translations/unit-005.json"
TABLE_IDS = [f"Table_01_01_{number:02}" for number in range(3, 10)]
SHAPES = [(2, 13), (2, 6), (2, 8), *[(4, 2)] * 4]
SELECTED = "fs-id1165137804204"
NEXT = "fs-id1165137503241"
FORBIDDEN = re.compile(r"[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def text(node):
    return "".join(node.itertext()).strip()


def sha256(path, normalize_xml=True):
    data = path.read_bytes()
    if normalize_xml and path.suffix == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def parse_reader(raw):
    return ET.fromstring(raw[raw.index("<html"):])


def by_id(document, identifier):
    matches = [node for node in document.iter() if node.get("id") == identifier]
    require(f"one_id:{identifier}", len(matches) == 1)
    return matches[0]


def parents(document):
    return {child: parent for parent in document.iter() for child in parent}


def rows(table):
    return [node for node in table.iter() if tag(node) in ("row", "tr")]


def prose(node, skip_links=False):
    value = node.text or ""
    for child in node:
        if tag(child) != "math" and not (skip_links and tag(child) in ("link", "a")):
            value += prose(child, skip_links)
        value += child.tail or ""
    return value


def source_specs(source):
    """Derive ordered keys from source, including the two pure-MathML headers."""
    parent = parents(source)
    specs = {}
    for node in source.iter():
        name = tag(node)
        if name in ("title", "label", "para", "item"):
            if name == "label" and not text(node):
                continue
            if name == "item":
                siblings = [child for child in parent[node] if tag(child) == "item"]
                key = f"{parent[node].get('id')}/item/{siblings.index(node) + 1}"
            else:
                key = node.get("id") or f"{parent[node].get('id')}/{name}"
            specs[key] = (name, node, None)
        if name == "table":
            identifier = node.get("id")
            specs[identifier + "/summary"] = ("summary", node, None)
            for row_number, row in enumerate(rows(node), 1):
                for column, entry in enumerate(row, 1):
                    header = tag(parent[row]) == "thead" or any(tag(c) == "emphasis" for c in entry)
                    header = header or (column == 1 and any(tag(c) == "math" for c in entry))
                    if header:
                        key = f"{identifier}/row/{row_number}/entry/{column}"
                        specs[key] = ("entry", entry, (identifier, row_number, column))
    return specs


def target_block(document, source, spec):
    name, node, location = spec
    if name == "entry":
        table, row, column = location
        return rows(by_id(document, table))[row - 1][column - 1]
    if node.get("id"):
        return by_id(document, node.get("id"))
    parent = parents(source)[node]
    rendered_parent = by_id(document, parent.get("id"))
    if name == "item":
        siblings = [child for child in parent if tag(child) == "item"]
        return rendered_parent.findall("li")[siblings.index(node)]
    heading = "h2" if name == "title" and tag(parent) == "section" else "h3"
    matches = rendered_parent.findall(heading)
    require(f"one_block_heading:{parent.get('id')}/{name}", len(matches) == 1)
    return matches[0]


def validate_boundary(source, manifest, check=require):
    witness = manifest["source_byte_witnesses"]
    checkout = WORKSPACE / witness["canonical_checkout_path"]
    pinned = WORKSPACE / witness["pinned_lf_witness_path"]
    check("canonical_raw_checkout_hash", sha256(checkout, False) == witness["canonical_checkout_sha256"])
    check("pinned_lf_module_hash", sha256(pinned, False) == manifest["full_module_sha256"])
    check("checkout_only_crlf_differs_from_pinned_lf", checkout.read_bytes().replace(b"\r\n", b"\n") == pinned.read_bytes())
    full = ET.parse(pinned).getroot()
    selected = by_id(full, SELECTED)
    check("canonical_subtree_exact_including_internal_whitespace", signature(source[0]) == signature(selected))
    parent = parents(full)
    boundary = manifest["selection_boundary"]
    check("selected_complete_section_and_cursor", len(source) == 1 and source[0].get("id") == SELECTED
          and manifest["selection_ids"] == [SELECTED] and manifest["next_source_id"] == NEXT)
    check("selected_parent_and_last_child", parent[selected].get("id") == boundary["parent_source_id"] == "fs-id1165133394710"
          and list(parent[selected])[-1] is selected)
    following_parent = parent[parent[selected]]
    following = list(following_parent)[list(following_parent).index(parent[selected]) + 1]
    check("next_section_is_outside_selected_parent", following.get("id") == boundary["following_element_id"] == NEXT
          and tag(following) == boundary["following_element_name"] == "section")
    descendants = [node.get("id") for node in selected.iter() if node.get("id")]
    check("first_and_last_selected_ids", boundary["first_selected_id"] == SELECTED
          and descendants[-1] == boundary["last_selected_descendant_id"] == "fs-id1165137844279")
    return {"selected": SELECTED, "following": NEXT, "parent": parent[selected].get("id"),
            "last_descendant": descendants[-1], "normalization": "CRLF to LF only for CNXML digest comparison"}


def validate_structure(document, source, check=require):
    ids = [node.get("id") for node in document.iter() if node.get("id")]
    originals = [node for node in source.iter() if node is not source and node.get("id")]
    source_ids = [node.get("id") for node in originals]
    check("unique_reader_ids", len(ids) == len(set(ids)))
    check("all_34_source_ids_in_exact_order", len(source_ids) == 34
          and [identifier for identifier in ids if identifier in source_ids] == source_ids)
    check("excerpt_wrapper_id_not_rendered", source.get("id") not in ids)

    def chain(node, parent):
        result = []
        while node in parent:
            node = parent[node]
            if node.get("id") in source_ids:
                result.append(node.get("id"))
        return result

    original_parent, rendered_parent = parents(source), parents(document)
    check("all_source_ancestor_chains_exact", all(chain(node, original_parent) ==
          chain(by_id(document, node.get("id")), rendered_parent) for node in originals))
    original_list = by_id(source, "fs-id1165137461155")
    target_list = by_id(document, original_list.get("id"))
    check("how_to_two_steps_remain_ordered", target_list.tag == "ol"
          and original_list.get("list-type") == "enumerated"
          and len(target_list.findall("li")) == len(list(original_list)) == 2)
    return source_ids


def validate_blocks(document, source, translation, manifest, check=require):
    specs, blocks = source_specs(source), translation["source_blocks"]
    check("all_41_translation_keys_exact_in_source_order", len(specs) == len(blocks) == 41 and list(specs) == list(blocks))
    labels = {item["id"]: item["local_label"] for item in manifest["references"]}
    numerals = {}
    for key, spec in specs.items():
        name, original, _ = spec
        rendered = target_block(document, source, spec)
        if name == "summary":
            check(f"summary_exact_translation:{key}", rendered.get("data-source-summary") == blocks[key])
            continue
        value = blocks[key]
        maths = [node for node in original.iter() if tag(node) == "math"]
        links = [node for node in original if tag(node) == "link"]
        check(f"math_placeholder_count_and_order:{key}", [int(i) for i in re.findall(r"\{\{math:(\d+)\}\}", value)] == list(range(len(maths))))
        check(f"link_placeholder_count_and_order:{key}", [int(i) for i in re.findall(r"\{\{link:(\d+)\}\}", value)] == list(range(len(links))))
        check(f"no_invented_child_placeholder:{key}", "{{child:" not in value)
        value = re.sub(r"\{\{math:\d+\}\}", "", value)
        value = re.sub(r"\{\{link:(\d+)\}\}", lambda match:
                       f'<a>جدول {labels[links[int(match[1])].get("target-id")]}</a>', value)
        fragment = ET.fromstring("<fragment>" + value + "</fragment>")
        check(f"rendered_translation_matches_key:{key}", prose(rendered).strip() == prose(fragment).strip())
        expected_numbers = re.findall(r"\d+", prose(original, True))
        actual_numbers = re.findall(r"\d+", prose(rendered, True))
        check(f"source_prose_numerals_exact:{key}", actual_numbers == expected_numbers)
        if expected_numbers:
            numerals[key] = expected_numbers
    return specs, numerals


def numeric(value):
    return int(value.replace("–", "-").replace("−", "-"))


def table_pairs(table):
    data = rows(table)
    if table.get("id") in TABLE_IDS[:3]:
        return [(numeric(text(x)), numeric(text(y))) for x, y in zip(list(data[0])[1:], list(data[1])[1:])]
    return [(numeric(text(row[0])), numeric(text(row[1]))) for row in data[1:]]


def summary_pairs(value):
    return [(numeric(x), numeric(y)) for x, y in re.findall(r"\(([–−-]?\d+),\s*([–−-]?\d+)\)", value)]


def validate_tables(document, source, translation, check=require):
    originals = [node for node in source.iter() if tag(node) == "table"]
    rendered = [node for node in document.iter("table") if "source-table" in node.get("class", "").split()]
    check("all_seven_source_and_rendered_tables_in_order", [node.get("id") for node in originals]
          == [node.get("id") for node in rendered] == TABLE_IDS)
    check("no_unnecessary_summary_overrides", not translation.get("table_summary_overrides"))
    specs = source_specs(source)
    source_parent, target_parent = parents(source), parents(document)
    report = []
    for original, target, shape in zip(originals, rendered, SHAPES):
        identifier = original.get("id")
        original_rows, target_rows = rows(original), rows(target)
        group = next(node for node in original if tag(node) == "tgroup")
        check(f"source_shape:{identifier}", len(original_rows) == shape[0]
              and int(group.get("cols")) == shape[1] and all(len(row) == shape[1] for row in original_rows))
        check(f"rendered_shape:{identifier}", len(target_rows) == shape[0] and all(len(row) == shape[1] for row in target_rows))
        check(f"table_ltr:{identifier}", target.get("dir") == "ltr")
        wrapper = target_parent[target]
        check(f"table_scroll_ltr_focusable:{identifier}", wrapper.get("dir") == "ltr"
              and wrapper.get("tabindex") == "0" and wrapper.get("role") == "region"
              and "source-table-scroll" in wrapper.get("class", "").split())
        for row_index, (original_row, target_row) in enumerate(zip(original_rows, target_rows), 1):
            for column, (entry, cell) in enumerate(zip(original_row, target_row), 1):
                key = f"{identifier}/row/{row_index}/entry/{column}"
                if key in specs:
                    scope = "col" if tag(source_parent[original_row]) == "thead" else "row"
                    check(f"header_type_scope_and_rtl:{key}", cell.tag == "th" and cell.get("scope") == scope and cell.get("dir") == "rtl")
                    value = re.sub(r"\{\{math:\d+\}\}", "", translation["source_blocks"][key])
                    check(f"header_translation:{key}", prose(cell).strip() == text(ET.fromstring("<fragment>" + value + "</fragment>")))
                    check(f"header_emphasis:{key}", len(cell.findall("em")) == sum(tag(child) == "emphasis" for child in entry))
                else:
                    check(f"table_data_exact:{key}", cell.tag == "td" and len(cell) == 0 and cell.text == text(entry))
                    check(f"table_data_ltr:{key}", cell.get("dir") == "ltr")
                check(f"source_alignment:{key}", (cell.get("style") == "text-align:center") == (entry.get("align") == "center"))
        summary = translation["source_blocks"][identifier + "/summary"]
        check(f"source_summary_and_accessible_label:{identifier}", target.get("data-source-summary") == target.get("aria-label") == summary)
        dimension_words = {(2, 13): ("Two rows and thirteen columns.", "دو قطاراں تے تیرہ کالم نیں۔"),
                           (2, 6): ("Two rows and six columns.", "دو قطاراں تے چھے کالم نیں۔"),
                           (2, 8): ("Two rows and eight columns.", "دو قطاراں تے اٹھ کالم نیں۔"),
                           (4, 2): ("Four rows and two columns.", "چار قطاراں تے دو کالم نیں۔")}
        english_dimensions, punjabi_dimensions = dimension_words[shape]
        check(f"summary_dimension_words_match_actual_shape:{identifier}", original.get("summary").startswith(english_dimensions)
              and summary.startswith(punjabi_dimensions))
        pairs = table_pairs(original)
        check(f"source_summary_pairs_match_cells:{identifier}", summary_pairs(original.get("summary")) == pairs)
        check(f"translated_summary_pairs_match_cells:{identifier}", summary_pairs(summary) == table_pairs(target) == pairs)
        # Keep negative sign spellings as well as numeric meaning in summaries.
        check(f"summary_numeric_spelling_and_order:{identifier}", re.findall(r"[–−-]?\d+", summary)
              == re.findall(r"[–−-]?\d+", original.get("summary")))
        report.append({"id": identifier, "rows": shape[0], "columns": shape[1],
                       "source_cells": [[text(cell) for cell in row] for row in original_rows], "pairs": pairs})
    return report


def validate_links(document, source, manifest, check=require):
    labels = {item["id"]: item["local_label"] for item in manifest["references"]}
    check("manifest_seven_table_labels_exact", labels == {identifier: f"1.1.{i}" for i, identifier in enumerate(TABLE_IDS, 3)}
          and all(item["kind"] == "table" for item in manifest["references"]))
    expected_all = []
    for original in source.iter():
        expected = ["#" + node.get("target-id") for node in original if tag(node) == "link"]
        if not expected:
            continue
        actual = by_id(document, original.get("id")).findall("a")
        check(f"source_link_targets:{original.get('id')}", [node.get("href") for node in actual] == expected)
        for ordinal, node in enumerate(actual):
            identifier = node.get("href")[1:]
            check(f"source_link_label:{original.get('id')}:{ordinal}", len(node) == 1 and node[0].tag == "bdi"
                  and node[0].get("dir") == "ltr" and node.text == "جدول " and text(node[0]) == labels[identifier])
        expected_all.extend(expected)
    actual_all = [node.get("href") for node in by_id(document, SELECTED).iter("a")]
    check("all_13_links_exact_in_source_order", len(expected_all) == 13 and actual_all == expected_all)
    return expected_all


def validate_math(document, source, check=require):
    source_maths = list(source.iter("{" + MATH + "}math"))
    rendered_maths = [node for node in document.iter() if tag(node) == "math"]
    check("all_14_math_trees_with_exact_namespace", len(source_maths) == len(rendered_maths) == 14
          and all(node.tag == "{" + MATH + "}math" for node in rendered_maths))
    specs = source_specs(source)
    owner_nodes = {node: key for key, (name, node, _) in specs.items() if name != "summary"}
    target_nodes = {target_block(document, source, spec): key for key, spec in specs.items() if spec[0] != "summary"}
    for equation in (node for node in source.iter() if tag(node) == "equation"):
        owner_nodes[equation] = equation.get("id")
        target_nodes[by_id(document, equation.get("id"))] = equation.get("id")

    def owner(node, parent, mapped):
        while node in parent:
            node = parent[node]
            if node in mapped:
                return mapped[node]
        raise AssertionError("math_has_source_block_or_cell_owner")

    source_parent, target_parent = parents(source), parents(document)
    owners = [owner(node, source_parent, owner_nodes) for node in source_maths]
    check("math_exact_block_cell_equation_owners_and_order", owners == [owner(node, target_parent, target_nodes) for node in rendered_maths])
    edits = []
    for index, (original, rendered) in enumerate(zip(source_maths, rendered_maths)):
        wrapper = target_parent[rendered]
        check(f"math_ltr_wrapper:{index}", wrapper.tag == "span" and wrapper.get("class") == "math-isolate" and wrapper.get("dir") == "ltr")
        check(f"math_wrapper_pure:{index}", len(wrapper) == 1 and wrapper[0] is rendered
              and wrapper.text in (None, "") and rendered.tail in (None, ""))
        edits.append(restore_math(original, rendered, index))
        check(f"exact_reversible_math_tree:{index}", True)
        for path, node in paths(original):
            if tag(node) == "mtext" and re.search(r"[A-Za-z]", node.text or ""):
                check(f"english_mtext_nbsp_retained:{index}:{path}", at_path(rendered, path).text == node.text)
    equations = [node for node in source.iter() if tag(node) == "equation"]
    check("two_display_equations", len(equations) == 2 and sum(node.get("display") == "block" for node in rendered_maths) == 2)
    for original in equations:
        target = by_id(document, original.get("id"))
        check(f"equation_container_pure:{original.get('id')}", target.get("dir") == "ltr" and target.text in (None, "")
              and len(target) == 1 and target[0].get("class") == "math-isolate" and target[0].tail in (None, "")
              and target[0].get("tabindex") == "0" and target[0].get("role") == "region")
    check("ledgers_only_on_math_roots", all(node in rendered_maths for node in document.iter() if LEDGER in node.attrib))
    check("exact_two_terminal_period_edits", sum(edits) == sum(bool(n) for n in edits) == 2
          and [(owners[i], n) for i, n in enumerate(edits) if n] == [("fs-id1165135191568", 1)] * 2)
    return {"trees": 14, "display_equations": 2, "text_edits": sum(edits), "source_owners_in_tree_order": owners}


def is_function(pairs):
    outputs = {}
    for x, y in pairs:
        outputs.setdefault(x, set()).add(y)
    return all(len(values) == 1 for values in outputs.values())


def validate_mathematics(document, source, check=require):
    data = {identifier: table_pairs(by_id(document, identifier)) for identifier in TABLE_IDS}
    original_data = {identifier: table_pairs(by_id(source, identifier)) for identifier in TABLE_IDS}
    check("rendered_pairs_equal_canonical_pairs", data == original_data)
    classifications = [is_function(data[identifier]) for identifier in TABLE_IDS]
    check("source_function_classifications", classifications == [True, True, False, True, True, False, True])
    check("nonleap_month_inputs_and_february", [x for x, _ in data[TABLE_IDS[0]]] == list(range(1, 13))
          and dict(data[TABLE_IDS[0]])[2] == 28)
    check("age_five_has_40_and_42_inches", [y for x, y in data[TABLE_IDS[2]] if x == 5] == [40, 42])
    check("table_eight_five_has_two_distinct_outputs", [y for x, y in data[TABLE_IDS[5]] if x == 5] == [2, 4])
    answer = text(by_id(document, "fs-id1165137401396"))
    check("worked_conclusion_preserves_two_functions_and_one_nonfunction",
          "جدول 1.1.6 تے جدول 1.1.7 فنکشن دی تعریف کردیاں نیں۔" in answer
          and "جدول 1.1.8 فنکشن دی تعریف نہیں کردی" in answer)
    check("age_height_source_nonfunction_conclusion", "ایہہ جدول فنکشن نہیں وکھاندی، کیوں جے" in text(by_id(document, "fs-id1165137561574")))
    check("table_eight_source_nonfunction_conclusion", "فنکشن نہیں وکھاندی" in text(by_id(document, "fs-id1165137656795")))
    check("finite_table_source_answer_yes_only", text(by_id(source, "fs-id1165137844279")) == "yes"
          and text(by_id(document, "fs-id1165137844279")) == "ہاں۔")
    equation_report = []
    for identifier, table_id, symbol in [("fs-id1165137404863", TABLE_IDS[3], "f"), ("fs-id1165137589116", TABLE_IDS[4], "g")]:
        target = by_id(document, identifier)
        compact = re.sub(r"\s+", "", text(target)).replace("−", "-")
        matches = re.findall(r"([fg])\((-?\d+)\)=(-?\d+)", compact)
        expected = [(symbol, str(x), str(y)) for x, y in data[table_id]]
        check(f"displayed_equation_matches_own_table:{identifier}", matches == expected)
        check(f"displayed_equation_has_only_source_relations:{identifier}", re.sub(r"([fg])\((-?\d+)\)=(-?\d+)", "", compact) == ",,and")
        equation_report.append({"source_equation": identifier, "table": table_id, "symbol": symbol, "pairs": data[table_id]})
    negative_cell = rows(by_id(document, TABLE_IDS[4]))[1][0]
    negative_summary = by_id(document, TABLE_IDS[4]).get("aria-label")
    negative_math = by_id(document, "fs-id1165137589116")
    check("three_negative_sign_source_spellings_retained", text(negative_cell) == "–3"
          and "(-3, 5)" in negative_summary and any(node.text == "−" for node in negative_math.iter("{" + MATH + "}mo")))
    bridge = by_id(document, "tables-bridge")
    check("bridge_explicitly_original", bridge.get("data-origin") == "original-bridge"
          and "ایہہ ماخذ دے ترجمے دا حصہ نہیں" in text(bridge))
    selected = by_id(document, SELECTED)
    check("bridge_outside_source_selection", bridge not in list(selected.iter()))
    key_rows = bridge.findall("./ul/li")
    expected_keys = [(TABLE_IDS[0], "f", 2), (TABLE_IDS[1], "g", 4), (TABLE_IDS[3], "f", 2), (TABLE_IDS[4], "g", 4)]
    check("four_source_local_function_examples", len(key_rows) == len(expected_keys))
    for row, (table_id, symbol, x) in zip(key_rows, expected_keys):
        labels = [node for node in row.iter("bdi") if "formula" in node.get("class", "").split()]
        check(f"bridge_function_example_bound_to_own_table:{table_id}", row.find("a").get("href") == "#" + table_id
              and len(labels) == 1 and re.sub(r"\s+", "", text(labels[0])) == f"{symbol}({x})={dict(data[table_id])[x]}")
    check("function_name_reuse_warning", "ساریاں مثالاں دے f یا g نوں اکّو فنکشن نہ سمجھو" in text(bridge))
    check("only_four_original_bridge_formula_examples", sum("formula" in node.get("class", "").split() for node in bridge.iter()) == 4)
    finite_link = next(node for node in bridge.iter("a") if node.get("href") == "#" + TABLE_IDS[6])
    finite_paragraph = parents(bridge)[finite_link]
    check("finite_table_no_inferred_formula_or_extrapolation", finite_paragraph.tag == "p" and len(finite_paragraph) == 1
          and "جدول وچ چند جوڑیاں ویکھ کے اکّو جبری قاعدہ لازمی طے نہیں ہوندا" in text(finite_paragraph)
          and "ایہہ جواب جدول توں باہر دیاں اِن پُٹ قدراں لئی کوئی نواں قاعدہ نہیں دیندا۔" in text(finite_paragraph)
          and not re.search(r"[0-9=^]", text(finite_paragraph)))
    check("bridge_three_signs_and_english_and_key", all(any(text(node) == token for node in bridge.iter("bdi")) for token in ("–3", "-3", "−3", "and", "in.")))
    check("original_scope_nonleap_inches_and_relation_disclosed", "غیر لیپ سال" in text(bridge)
          and "قد سینٹی میٹراں وچ نہیں بدلے" in text(bridge)
          and "ترتیب وار جوڑیاں دے تعلق وجوں لکھ سکدے آں" in text(bridge))
    return {"function_classifications": dict(zip(TABLE_IDS, classifications)), "source_equations": equation_report,
            "finite_table_scope": "only displayed pairs; no unique formula or extrapolation is inferred"}


def validate_directions(document, check=require):
    parent = parents(document)

    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = parent.get(node)
        return None

    check("all_bdi_explicit_ltr", all(node.get("dir") == "ltr" for node in document.iter("bdi")))
    check("all_english_language_lanes_ltr", all(direction(node) == "ltr" for node in document.iter() if node.get("lang") == "en"))
    for node in document.find("body").iter():
        for fragment in [node.text or "", *[child.tail or "" for child in node]]:
            if re.search(r"[A-Za-z0-9]", fragment):
                require("visible_latin_and_numbers_ltr", direction(node) == "ltr")
    check("visible_latin_and_numbers_ltr", True)
    local = []
    for node in document.iter():
        for attribute in ("href", "src"):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
            parsed = urlsplit(value)
            if parsed.scheme in ("http", "https", "mailto"):
                continue
            require("supported_local_reference", not parsed.scheme and not parsed.netloc)
            target = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            require(f"local_file_exists:{value}", target.is_file())
            if parsed.fragment:
                linked = document if target == READER.resolve() else parse_reader(target.read_text(encoding="utf-8"))
                by_id(linked, unquote(parsed.fragment))
            local.append(value)
    check("all_local_files_and_fragment_links_resolve", True)
    check("previous_unit_navigation", any(node.get("href") == "unit-004.html" for node in document.findall(".//nav/a")))
    return local


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    translation = json.loads(TRANSLATION.read_text(encoding="utf-8"))
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    inputs = [TRANSLATION, MANIFEST, excerpt, BASE / "qa/unit-005-language-notes.md", BASE / "scripts/build.py",
              BASE / "scripts/qa_notation.py", Path(__file__).resolve(), BASE / "styles/reader.css",
              BASE / "terminology.tsv", BASE / "provenance/ATTRIBUTION.md", BASE / "canon/examples.json"]
    initial = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    command = [sys.executable, str(BASE / "scripts/build.py"), "--unit", "005"]
    subprocess.run(command, check=True)
    first = READER.read_bytes()
    subprocess.run(command, check=True)
    require("deterministic_reader_build", first == READER.read_bytes())
    document = parse_reader(first.decode("utf-8"))
    checks = ["deterministic_reader_build"]

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    check("frozen_lf_normalized_excerpt_hash", sha256(excerpt) == manifest["excerpt_sha256"])
    check("exact_locale_unit_and_rtl", manifest["unit"] == translation["unit"] == "PNB-005"
          and translation["locale"] == document.get("lang") == "pnb-Arab-PK" and document.get("dir") == "rtl")
    for path in [*inputs, READER]:
        check(f"unicode_clean:{path.relative_to(BASE).as_posix()}", not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", first.decode("utf-8")))
    check("no_source_images_media_or_footnotes", not manifest["images"]
          and not any(tag(node) in ("image", "media", "figure", "footnote") for node in source.iter()))
    check("no_reader_images_or_footnotes", not list(document.iter("img"))
          and not any("source-footnote" in node.get("class", "").split() or "source-endnotes" in node.get("class", "").split() for node in document.iter()))
    check("bounded_translation_disclosure", "پورے حصے دا ترجمہ نہیں" in first.decode("utf-8"))
    boundary = validate_boundary(source, manifest, check)
    ids = validate_structure(document, source, check)
    specs, numerals = validate_blocks(document, source, translation, manifest, check)
    tables = validate_tables(document, source, translation, check)
    links = validate_links(document, source, manifest, check)
    mathematics = validate_math(document, source, check)
    examples = validate_mathematics(document, source, check)
    local = validate_directions(document, check)
    bridge = by_id(document, "tables-bridge")
    check("original_bridge_exactly_rendered_from_separate_manuscript", signature(bridge) == signature(ET.fromstring(translation["bridge_after_html"])))
    check("source_statistics_match_observations", manifest["source_statistics"] == {
        "identified_nodes": len(ids), "translation_blocks": len(specs), "tables": len(tables),
        "mathml_trees": mathematics["trees"], "display_equations": mathematics["display_equations"],
        "links": len(links), "images": 0, "footnotes": 0})

    def reject(name, mutate, validate, prefix):
        mutant = copy.deepcopy(document)
        mutate(mutant)
        try:
            validate(mutant)
        except AssertionError as error:
            check(name, str(error).startswith(prefix))
        else:
            raise AssertionError(name + ":mutation_not_rejected")

    def changed_cell(mutant):
        rows(by_id(mutant, TABLE_IDS[0]))[1][2].text = "29"

    def changed_number(mutant):
        next(node for node in mutant.iter("{" + MATH + "}mn")).text = "999"

    def changed_ledger(mutant):
        math = next(node for node in mutant.iter("{" + MATH + "}math") if node.get(LEDGER))
        ledger = json.loads(math.get(LEDGER))
        ledger[0]["old"] = ","
        math.set(LEDGER, json.dumps(ledger))

    def internal_comma(mutant):
        index, path, old = next((i, path, node.text) for i, math in enumerate(source.iter("{" + MATH + "}math"))
                               for path, node in paths(math) if tag(node) == "mo" and node.text == ","
                               and path not in allowed_punctuation_edits(math))
        math = list(mutant.iter("{" + MATH + "}math"))[index]
        at_path(math, path).text = ""
        math.set(LEDGER, json.dumps([{"path": list(path), "old": old, "new": ""}]))

    def bridge_overreach(mutant):
        bridge = by_id(mutant, "tables-bridge")
        link = next(node for node in bridge.iter("a") if node.get("href") == "#" + TABLE_IDS[6])
        paragraph = parents(bridge)[link]
        ET.SubElement(paragraph, "bdi", {"dir": "ltr", "class": "formula"}).text = "f(4) = 10000"

    def bridge_claim_overreach(mutant):
        bridge = by_id(mutant, "tables-bridge")
        link = next(node for node in bridge.iter("a") if node.get("href") == "#" + TABLE_IDS[6])
        link.tail = link.tail.replace("کوئی نواں قاعدہ نہیں دیندا", "نواں قاعدہ دیندا")

    reject("mutation_table_data_rejected", changed_cell, lambda d: validate_tables(d, source, translation), "table_data_exact:")
    reject("mutation_table_link_target_rejected", lambda d: by_id(d, "fs-id1165137761188").find("a").set("href", "#" + TABLE_IDS[1]),
           lambda d: validate_links(d, source, manifest), "source_link_targets:")
    reject("mutation_math_number_rejected", changed_number, lambda d: validate_math(d, source), "math_tree_exactly_reconstructed:")
    reject("mutation_math_wrapper_text_rejected", lambda d: setattr(next(d.iter("{" + MATH + "}math")), "tail", "=999"),
           lambda d: validate_math(d, source), "math_wrapper_pure:")
    reject("mutation_false_punctuation_ledger_rejected", changed_ledger, lambda d: validate_math(d, source), "ledger_old_matches_source:")
    reject("mutation_reversible_internal_comma_deletion_rejected", internal_comma,
           lambda d: validate_math(d, source), "punctuation_edit_position_whitelisted:")
    reject("mutation_function_conclusion_rejected", lambda d: setattr(by_id(d, "fs-id1165137844279"), "text", "نہیں۔"),
           lambda d: validate_mathematics(d, source), "finite_table_source_answer_yes_only")
    reject("mutation_bridge_extrapolation_rejected", bridge_overreach,
           lambda d: validate_mathematics(d, source), "only_four_original_bridge_formula_examples")
    reject("mutation_bridge_claim_of_rule_rejected", bridge_claim_overreach,
           lambda d: validate_mathematics(d, source), "finite_table_no_inferred_formula_or_extrapolation")
    check("detached_mutations_leave_reader_unchanged", first == READER.read_bytes())
    final = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    check("checked_inputs_stable_during_run", final == initial)
    final[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {
        "unit": "PNB-005", "status": "structural_pass_linguistic_and_visual_review_separate",
        "translated_blocks": len(specs), "source_block_keys": list(specs), "source_ids_preserved": len(ids), "source_ids": ids,
        "boundary": boundary, "tables": tables, "math": mathematics, "source_link_targets": links,
        "source_prose_numerals": numerals, "example_mathematics": examples, "local_reference_count": len(local),
        "canon_consultation": {"method": "Actual local R2/R3 prose loci read during implementation, not regenerated by QA runs",
            "examples": ["C07", "C09", "C10", "C11"],
            "application": "Row/column location, reminder, explicit qualification and reason-giving wording checked; no terminology certification inferred."},
        "checks": checks, "hashes": final,
        "limitations": [
            "Only this declared section is verified; the full module and all five assigned books remain incomplete.",
            "Exact text/key matching and lexical conclusion guards do not prove idiomatic Punjabi or constitute native-speaker/educator approval.",
            "MathML restoration uses the separately hashed qa_notation.py policy, independent of the renderer's punctuation implementation.",
            "Summary attributes are plain text and cannot carry inline bidi markup; screen-reader pronunciation and direction require separate accessibility review.",
            "Table data and formula mathematics are checked from rendered values; the finite final table establishes no unique formula or values outside its listed inputs.",
            "Focusability and RTL/LTR markup are verified structurally, not keyboard interaction, viewport layout, shaping, font portability or visual scrolling behavior.",
            "External links are preserved but not network-tested. LF normalization applies only to CNXML digest comparison; no source archive is changed.",
        ],
    }
    (BASE / "qa/structural-005.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(checks)} checks; 41 translated blocks; 34 source IDs; 7 tables; 14 MathML trees; 9 detached mutations")


if __name__ == "__main__":
    main()
