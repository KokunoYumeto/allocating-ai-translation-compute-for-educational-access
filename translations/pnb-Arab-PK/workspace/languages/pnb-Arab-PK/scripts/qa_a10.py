"""Source-bound A10-001 structural QA, with detached negative tests only.

This checks one declared opening selection, not whole-book completion or
native-language/accessibility approval. Source alt errors remain visible in
the provenance and are explained by separately labeled original notes.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import copy
import csv
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

from qa_notation import MATH, jpeg_dimensions, signature


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
MANIFEST = BASE / "source-excerpts/manifest-a10-001.json"
TRANSLATION = BASE / "translations/a10-unit-001.json"
READER = BASE / "reader/a10-unit-001.html"
NOTICES = BASE / "provenance/a10-unit-001-component-notices.json"
SECTION = "fs-id1170655083568"
MIXED = "fs-id1170654968077"
NESTED_MEDIA = "fs-id1170655112880"
DIRECT_NOTE = "fs-id1166423891565"
PARTS = [f"({letter})" for letter in "abcde"]
FORBIDDEN = re.compile(r"[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]")
NUMERALS = re.compile(r"[0-9]+(?:,[0-9]{3})*")


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


def parse_fragment(raw):
    return ET.fromstring("<fragment>" + re.sub(r"<br\s*/?>", "<br />", raw) + "</fragment>")


def parse_reader(raw):
    # The reader is HTML, not XHTML. Only self-close its actual void elements
    # in memory for the XML inspection tree; do not repair structural nesting.
    raw = raw[raw.index("<html"):]
    raw = re.sub(r"<(meta|img|br)\b([^<>]*?)(?<!/)>", lambda match: "<" + match[1] + match[2] + " />", raw)
    return ET.fromstring(raw)


def parents(document):
    return {child: parent for parent in document.iter() for child in parent}


def by_id(document, identifier):
    found = [node for node in document.iter() if node.get("id") == identifier]
    require(f"one_id:{identifier}", len(found) == 1)
    return found[0]


def source_specs(source):
    parent = parents(source)
    specs = {}
    for node in source.iter():
        name = tag(node)
        if name not in ("para", "title", "caption", "item", "media", "note"):
            continue
        if name == "note" and (len(node) or not (node.text or "").strip()):
            continue
        if name == "item":
            siblings = [child for child in parent[node] if tag(child) == "item"]
            key = f"{parent[node].get('id')}/item/{siblings.index(node) + 1}"
        else:
            key = node.get("id") or f"{parent[node].get('id')}/{name}"
        if name == "media":
            key += "/alt"
        specs[key] = (name, node)
    return specs


def target_block(document, source, spec):
    name, node = spec
    if node.get("id"):
        return by_id(document, node.get("id"))
    parent = parents(source)[node]
    target = by_id(document, parent.get("id"))
    if name == "item":
        siblings = [child for child in parent if tag(child) == "item"]
        return target.findall("li")[siblings.index(node)]
    wanted = "figcaption" if name == "caption" else "h2" if tag(parent) == "section" else "h3"
    found = target.findall(wanted)
    require(f"one_source_heading_or_caption:{parent.get('id')}/{name}", len(found) == 1)
    return found[0]


def source_prose(node):
    value = node.text or ""
    for child in node:
        if tag(child) not in ("math", "media", "link", "span") or (tag(child) == "span" and child.get("class") != "token"):
            value += source_prose(child)
        value += child.tail or ""
    return value


def without_embedded(node, skip_links=False):
    """Rendered prose excluding only independently identifiable source media."""
    value = node.text or ""
    for child in node:
        classes = child.get("class", "").split()
        omit = tag(child) == "math" or "source-media" in classes or child.get("data-source-child")
        omit = omit or (skip_links and tag(child) == "a")
        if not omit:
            value += without_embedded(child, skip_links)
        value += child.tail or ""
    return value


def validate_source(source, manifest, check=require):
    original_path = WORKSPACE / manifest["canonical_local_path"]
    original_bytes = original_path.read_bytes()
    check("canonical_module_raw_hash_and_size", len(original_bytes) == manifest["full_module_bytes"]
          and sha256(original_path, False) == manifest["full_module_sha256"])
    check("canonical_module_git_blob_sha1", hashlib.sha1(b"blob " + str(len(original_bytes)).encode() + b"\0" + original_bytes).hexdigest()
          == manifest["canonical_git_blob_sha1"])
    original = ET.fromstring(original_bytes)
    content = next(node for node in original if tag(node) == "content")
    check("selected_three_roots_in_canonical_order", [node.get("id") for node in source]
          == [node.get("id") for node in list(content)[:3]] == manifest["selection_ids"])
    prefix = copy.deepcopy(by_id(original, SECTION))
    prefix[:] = list(prefix)[:13]
    expected = [content[0], content[1], prefix]
    check("all_selected_subtrees_canonical_exact", all(signature(actual) == signature(wanted) for actual, wanted in zip(source, expected)))
    selected = by_id(source, SECTION)
    full_section = by_id(original, SECTION)
    check("section_thirteen_child_prefix_and_next_boundary", len(selected) == manifest["section_direct_children_included"] == 13
          and selected[-1].get("id") == manifest["scope_through_inclusive"] == "fs-id1170654885628"
          and full_section[13].get("id") == manifest["next_source_id"] == "fs-id1170655113270")
    check("selection_does_not_claim_whole_assignment", manifest["whole_assignment_complete"] is False
          and [item["module"] for item in manifest["earlier_collection_items_still_pending"]] == ["m82630", "m82451"])
    counts = manifest["source_counts"]
    kinds = {name: sum(tag(node) == name for node in source.iter()) for name in ("para", "title", "caption", "media", "item", "math", "mtable", "table", "figure", "image", "link", "note", "example", "exercise", "solution", "term", "newline")}
    mapping = {"para": "paragraphs", "title": "titles", "caption": "captions", "media": "media",
               "item": "list_items", "math": "mathml_trees", "mtable": "mathml_tables", "table": "cnxml_tables",
               "figure": "figures", "image": "images", "link": "source_links", "note": "notes",
               "example": "examples", "exercise": "exercises", "solution": "solutions", "term": "terms", "newline": "newlines"}
    check("declared_source_counts_equal_actual_selection", all(kinds[key] == counts[value] for key, value in mapping.items())
          and counts["direct_text_notes"] == 1 and counts["try_it_notes"] == 2 and counts["media_alt_blocks"] == 3)
    return kinds


def validate_structure(document, source, manifest, check=require):
    source_ids = [node.get("id") for node in source.iter() if node is not source and node.get("id")]
    ids = [node.get("id") for node in document.iter() if node.get("id")]
    check("unique_reader_ids", len(ids) == len(set(ids)))
    check("all_43_source_ids_in_exact_order", len(source_ids) == 43 and source_ids == manifest["source_ids_in_document_order"]
          and [identifier for identifier in ids if identifier in source_ids] == source_ids)
    check("excerpt_root_not_rendered", source.get("id") not in ids)
    original_parent, target_parent = parents(source), parents(document)

    def ancestry(node, parent):
        result = []
        while node in parent:
            node = parent[node]
            if node.get("id") in source_ids:
                result.append(node.get("id"))
        return result

    check("source_id_ancestor_chains_preserved", all(ancestry(node, original_parent) == ancestry(by_id(document, node.get("id")), target_parent)
          for node in source.iter() if node is not source and node.get("id")))
    check("declared_retained_id_count_matches_selection", manifest["source_counts"]["retained_source_ids_excluding_excerpt_root"] == len(source_ids))
    terms = [node for node in source.iter() if tag(node) == "term"]
    check("five_term_ids_in_source_order", [node.get("id") for node in terms] == manifest["renderer_contract"]["inline_term_ids"])
    for term in terms:
        target = by_id(document, term.get("id"))
        check(f"term_is_visible_span:{term.get('id')}", target.tag == "span" and bool(text(target)))
        if term.get("class") == "no-emphasis":
            current = target
            bold = False
            while current in target_parent and current.get("id") not in manifest["selection_ids"]:
                current = target_parent[current]
                bold = bold or current.tag in ("strong", "b")
            check(f"source_no_emphasis_term_not_bold:{term.get('id')}", not bold)
    check("zero_source_cnxml_or_mathml_tables", not any(tag(node) in ("table", "mtable") for node in source.iter()))
    check("bridge_tables_not_confused_with_source_tables", not list(by_id(document, SECTION).iter("table"))
          and not any("source-table" in node.get("class", "").split() for node in document.iter("table")))
    original_note = by_id(source, DIRECT_NOTE)
    rendered_note = by_id(document, DIRECT_NOTE)
    check("direct_text_activity_note_retained", not len(original_note) and "Number Line-Part 1" in text(original_note)
          and rendered_note.tag == "aside" and "Manipulative Mathematics" in text(rendered_note)
          and "سرگرمی" in text(rendered_note))
    solution = by_id(document, "fs-id1170655022351")
    check("explicit_source_solution_title_once", [text(node) for node in solution if node.tag in ("h2", "h3")] == ["حل"])
    return source_ids


def validate_mixed_and_newlines(document, source, check=require):
    mixed = by_id(document, MIXED)
    media = by_id(document, NESTED_MEDIA)
    parent = parents(document)
    check("mixed_paragraph_valid_block_container", mixed.tag == "div" and media in list(mixed.iter()))
    forbidden_blocks = {"div", "p", "section", "aside", "figure", "table", "ol", "ul", "h2", "h3"}
    check("no_invalid_block_inside_paragraph", all(not any(child.tag in forbidden_blocks for child in node.iter() if child is not node) for node in document.iter("p")))
    children = list(mixed)
    newline_positions = [index for index, node in enumerate(children) if node.tag == "br"]
    media_positions = [index for index, node in enumerate(children) if media is node or media in list(node.iter())]
    check("newline_precedes_nested_media_once", len(newline_positions) == len(media_positions) == 1
          and newline_positions[0] < media_positions[0])
    current = media
    chain = []
    while current in parent and current is not mixed:
        current = parent[current]
        chain.append(current)
    check("nested_media_has_no_invented_figure", not any(node.tag == "figure" for node in chain))
    breaks = []
    for original in source.iter():
        expected = sum(tag(child) == "newline" for child in original)
        if expected:
            target = by_id(document, original.get("id"))
            actual = sum(child.tag == "br" for child in target)
            check(f"source_newline_count:{original.get('id')}", actual == expected)
            breaks.append({"source_id": original.get("id"), "newlines": expected})
    check("all_five_source_newlines_present", sum(item["newlines"] for item in breaks) == 5
          and sum(node.tag == "br" for node in by_id(document, SECTION).iter()) == 5)
    return breaks


def validate_blocks(document, source, translation, manifest, check=require):
    specs = source_specs(source)
    blocks = translation["source_blocks"]
    check("all_30_keys_in_exact_source_order", len(specs) == len(blocks) == 30 and list(specs) == list(blocks))
    check("declared_translation_block_count_matches_selection", manifest["source_counts"]["translated_text_blocks"] == len(specs))
    labels = {item["figure_id"]: item["local_label"] for item in manifest["images"] if item["figure_id"]}
    numerals = {}
    for key, spec in specs.items():
        name, original = spec
        target = target_block(document, source, spec)
        value = blocks[key]
        if name == "media":
            check(f"source_alt_translation_exact:{key}", target.tag == "img" and target.get("alt") == value)
            original_text, rendered_text = original.get("alt"), target.get("alt")
        else:
            own_math = [node for node in original.iter() if tag(node) == "math"]
            links = [node for node in original if tag(node) == "link"]
            children = [node for node in original if tag(node) == "media"]
            for placeholder, expected in (("math", own_math), ("link", links), ("child", children)):
                check(f"{placeholder}_placeholder_order:{key}", [int(index) for index in re.findall(r"\{\{" + placeholder + r":(\d+)\}\}", value)] == list(range(len(expected))))
            value = re.sub(r"\{\{math:\d+\}\}|\{\{child:\d+\}\}", "", value)
            value = re.sub(r"\{\{link:(\d+)\}\}", lambda match: '<a>شکل ' + labels[links[int(match[1])].get("target-id")] + '</a>', value)
            expected = parse_fragment(value)
            check(f"source_translation_exact:{key}", without_embedded(target).strip() == text(expected))
            original_text = source_prose(original)
            rendered_text = without_embedded(target, True)
            expected_terms = [node.get("id") for node in expected.iter() if node.get("id")]
            actual_terms = [node.get("id") for node in target.iter() if node.get("id", "").startswith("term-")]
            check(f"inline_term_order:{key}", actual_terms == expected_terms)
        source_numbers = NUMERALS.findall(original_text)
        check(f"source_numerals_exact:{key}", NUMERALS.findall(rendered_text) == source_numbers)
        if source_numbers:
            numerals[key] = source_numbers
    return specs, numerals


def validate_math(document, source, check=require):
    original = list(source.iter("{" + MATH + "}math"))
    rendered = [node for node in document.iter() if tag(node) == "math"]
    check("two_spacing_only_math_trees", len(original) == len(rendered) == 2
          and all([tag(n) for n in node.iter()] == ["math", "mrow", "mspace"] for node in original))
    target_parent = parents(document)
    source_parent = parents(source)
    owners = []
    for index, (src, target) in enumerate(zip(original, rendered)):
        wrapper = target_parent[target]
        owner = target_parent[wrapper]
        owners.append(source_parent[src].get("id"))
        check(f"math_source_owner:{index}", owner.get("id") == source_parent[src].get("id"))
        check(f"pure_ltr_math_wrapper:{index}", wrapper.tag == "span" and wrapper.get("class") == "math-isolate"
              and wrapper.get("dir") == "ltr" and len(wrapper) == 1 and wrapper.text in (None, "") and target.tail in (None, ""))
        check(f"math_root_namespace_and_ltr:{index}", target.tag == "{" + MATH + "}math" and target.get("dir") == "ltr")
        clone = copy.deepcopy(target)
        clone.attrib.pop("dir")
        check(f"math_tree_exact_without_any_text_edit:{index}", signature(clone) == signature(src))
    check("no_punctuation_edit_ledgers_needed", not any("data-source-text-edits" in node.attrib or "data-source-punctuation" in node.attrib for node in document.iter()))
    return {"trees": 2, "source_owners_in_tree_order": owners, "content": "spacing-only mrow/mspace width=1.5em; number and answer checks are separate"}


def split_parts(value, source=False):
    if source:
        value = re.sub(r"[ⓐ-ⓔ]", lambda match: "(" + unicodedata.normalize("NFKC", match[0]) + ")", value)
    tokens = list(re.finditer(r"\([a-e]\)", value))
    return [(match[0], value[match.end():tokens[index + 1].start() if index + 1 < len(tokens) else len(value)].strip()) for index, match in enumerate(tokens)]


def validate_parts(document, source, check=require):
    originals = [node for node in source.iter() if tag(node) == "span" and node.get("class") == "token"]
    source_parent = parents(source)
    source_tokens = ["(" + unicodedata.normalize("NFKC", text(node)) + ")" for node in originals]
    rendered = [node for node in by_id(document, SECTION).iter("bdi") if re.match(r"^\([a-e]\)", text(node))]
    check("all_30_parts_in_exact_order", len(originals) == len(rendered) == 30
          and [re.match(r"^\([a-e]\)", text(node))[0] for node in rendered] == source_tokens == PARTS * 6)
    check("all_part_tokens_explicit_ltr", all(node.get("dir") == "ltr" for node in rendered))
    parent_groups = list(dict.fromkeys(source_parent[node] for node in originals))
    specs = source_specs(source)
    for original in parent_groups:
        key = next(key for key, (_, node) in specs.items() if node is original)
        target = target_block(document, source, specs[key])
        expected = [label for label, _ in split_parts(text(original), True)]
        actual = [label for label, _ in split_parts(text(target))]
        check(f"part_order_in_owner:{key}", actual == expected)
    source_list = by_id(source, "fs-id1166421427575")
    target_list = by_id(document, source_list.get("id"))
    check("five_question_items_keep_list_semantics", target_list.tag == "ol" and len(target_list.findall("li")) == len(source_list) == 5
          and "source-parts" in target_list.get("class", "").split() and target_list.get("role") == "list")
    return source_tokens


def english_place(value):
    digit = None
    matched = re.match(r"^The (\d) is in the (.+?) place\.$", value)
    if matched:
        digit, value = int(matched[1]), matched[2]
    normalized = value.replace("-", " ").strip()
    positions = {"ones": 0, "tens": 1, "hundreds": 2, "thousands": 3, "ten thousands": 4,
                 "hundred thousands": 5, "millions": 6, "ten millions": 7, "hundred millions": 8,
                 "billions": 9, "ten billions": 10, "hundred billions": 11}
    require("source_place_name_recognized", normalized in positions)
    return positions[normalized], digit


def punjabi_place(value):
    digit = None
    matched = re.match(r"^ہندسہ\s+(\d)\s+(.+)$", value)
    if matched:
        digit, value = int(matched[1]), matched[2]
    value = re.sub(r"(?: دی جگہ اُتے اے۔| والی جگہ اُتے اے۔)$", "", value)
    positions = {"اکائیاں": 0, "دہائیاں": 1, "سینکڑے": 2, "ہزاراں": 3, "دس ہزار": 4,
                 "سو ہزار": 5, "ملیناں": 6, "دس ملین": 7, "سو ملین": 8, "بلیناں": 9}
    require("rendered_place_name_recognized", value in positions)
    return positions[value], digit


def validate_answers(document, source, check=require):
    report = []
    for exercise in (node for node in source.iter() if tag(node) == "exercise"):
        original_problem = next(node for node in exercise if tag(node) == "problem")
        original_solution = next(node for node in exercise if tag(node) == "solution")
        target_problem = by_id(document, original_problem.get("id"))
        target_solution = by_id(document, original_solution.get("id"))
        number_node = next(node for node in original_problem if tag(node) == "para")
        expected_number = NUMERALS.findall(text(number_node))
        actual_number = NUMERALS.findall(text(by_id(document, number_node.get("id"))))
        identifier = exercise.get("id")
        check(f"exercise_source_number:{identifier}", len(expected_number) == 1 and actual_number == expected_number)
        number = int(actual_number[0].replace(",", ""))
        questions = split_parts(text(original_problem), True)
        target_questions = split_parts(text(target_problem))
        answers = split_parts(text(original_solution), True)
        target_answers = split_parts(text(target_solution))
        check(f"five_question_answer_pairs:{identifier}", len(questions) == len(target_questions) == len(answers) == len(target_answers) == 5)
        pairs = []
        for (label, question), (target_label, target_question), (answer_label, answer), (target_answer_label, target_answer) in zip(questions, target_questions, answers, target_answers):
            check(f"question_answer_label_association:{identifier}:{label}", label == target_label == answer_label == target_answer_label)
            require(f"source_question_digit:{identifier}:{label}", re.fullmatch(r"\d", question) is not None)
            check(f"rendered_question_digit:{identifier}:{label}", target_question == question)
            power, answer_digit = english_place(answer)
            target_power, target_answer_digit = punjabi_place(target_answer)
            check(f"answer_position_source_exact:{identifier}:{label}", target_power == power and target_answer_digit == answer_digit)
            check(f"displayed_digit_at_displayed_answer_position:{identifier}:{label}", number // (10 ** target_power) % 10 == int(target_question)
                  and (target_answer_digit is None or target_answer_digit == int(target_question)))
            pairs.append({"part": label, "digit": int(target_question), "place_power_of_ten": target_power})
        report.append({"source_exercise": identifier, "number": actual_number[0], "pairs": pairs})
    check("one_example_two_try_its_mathematically_checked", len(report) == 3)
    return report


def validate_inline_part_groups(document, source, translation, check=require):
    """Verify each mobile grouping before removing only its presentation span.

    This derives the five owners and 25 labels from actual source token nodes.
    Flattening a wrapper must reproduce every saved child/text/tail exactly;
    each wrapper must also contain the complete answer, not just its label.
    """
    owners = []
    for original in source.iter():
        tokens = [node for node in original if tag(node) == "span" and node.get("class") == "token"]
        if tag(original) == "para" and tokens:
            owners.append((original, tokens))
    check("five_source_inline_part_owners", len(owners) == 5)
    observed = []
    for original, tokens in owners:
        identifier = original.get("id")
        target = by_id(document, identifier)
        labels = ["(" + unicodedata.normalize("NFKC", text(node)) + ")" for node in tokens]
        expected_fragment = parse_fragment(translation["source_blocks"][identifier])
        expected_parts = split_parts(text(expected_fragment))
        wrappers = [node for node in target if node.tag == "span" and "source-inline-part" in node.get("class", "").split()]
        check(f"all_five_inline_parts_grouped:{identifier}", len(wrappers) == len(tokens) == len(expected_parts) == 5)
        for index, (wrapper, label, expected) in enumerate(zip(wrappers, labels, expected_parts)):
            check(f"source_part_wrapper_identity:{identifier}:{index}", wrapper.attrib == {"class": "source-inline-part", "data-source-part": label[1]}
                  and expected[0] == label)
            check(f"complete_part_inside_wrapper:{identifier}:{label}", split_parts(text(wrapper)) == [expected])
            check(f"source_newlines_outside_part_wrapper:{identifier}:{label}", not list(wrapper.iter("br")))
        clone = copy.deepcopy(target)
        for wrapper in list(clone):
            if wrapper.tag != "span" or wrapper.get("class") != "source-inline-part":
                continue
            index = list(clone).index(wrapper)
            if wrapper.text is not None:
                if index:
                    clone[index - 1].tail = (clone[index - 1].tail or "") + wrapper.text
                else:
                    clone.text = (clone.text or "") + wrapper.text
            children = list(wrapper)
            require("verified_part_wrapper_has_inline_children", bool(children))
            clone.remove(wrapper)
            for offset, child in enumerate(children):
                clone.insert(index + offset, child)
            if wrapper.tail is not None:
                children[-1].tail = (children[-1].tail or "") + wrapper.tail
        content = lambda node: (node.text, tuple((signature(child), child.tail) for child in node))
        check(f"grouping_preserves_exact_markup_text_whitespace_and_breaks:{identifier}", content(clone) == content(expected_fragment))
        observed.append({"source_id": identifier, "parts": labels})
    all_wrappers = [node for node in document.iter("span") if "source-inline-part" in node.get("class", "").split()]
    expected_owner_ids = {node.get("id") for node, _ in owners}
    parent = parents(document)
    check("exact_25_inline_groups_only_in_source_token_paragraphs", len(all_wrappers) == 25
          and all(parent[node].get("id") in expected_owner_ids for node in all_wrappers))
    check("source_list_items_not_regrouped", not any("source-inline-part" in node.get("class", "").split()
          for node in by_id(document, "fs-id1166421427575").iter()))
    style = text(document.find("head/style"))
    check("inline_part_group_is_inline_block", re.search(r"\.source-inline-part\s*\{[^}]*display\s*:\s*inline-block\b", style) is not None)
    return observed


def validate_source_discrepancies(document, source, translation, check=require):
    source_alt = by_id(source, "fs-id1170655200451").get("alt")
    target_alt = by_id(document, "fs-id1170655200451").get("alt")
    check("source_number_name_error_retained_in_translated_alt", "two hundred seventy-nine thousand" in source_alt
          and "دو سو اُناسی ہزار" in target_alt and "دو سو اَٹھہتر ہزار" not in target_alt)
    source_nested_alt = by_id(source, NESTED_MEDIA).get("alt")
    target_nested_alt = by_id(document, NESTED_MEDIA).get("alt")
    check("source_absent_title_row_claim_retained_in_alt", 'header row, labeled “Place Value”' in source_nested_alt
          and "جدول دی اُتلی سرخی «جگہ دی قدر» اے" in target_nested_alt)
    bridge = by_id(document, "a10-place-value-bridge")
    check("corrections_explicitly_original", bridge.get("data-origin") == "original-bridge"
          and "ایہہ ماخذ دے متن دا حصہ نہیں" in text(bridge)
          and bridge not in list(by_id(document, SECTION).iter()))
    check("number_name_correction_and_evidence_disclosed", "دو سو اُناسی ہزار" in text(bridge)
          and "دو سو اَٹھہتر ہزار" in text(bridge)
          and "ایہہ درستی ساڈی ولوں وکھری دَسی گئی اے؛ اصل ماخذ نہیں بدلیا گیا" in text(bridge)
          and "انڈونیشی ترجمہ وی اَٹھہتر آکھدا اے" in text(bridge))
    check("image_title_row_discrepancy_disclosed", "اصل تصویر وچ ایہہ وکھری اُتلی سطر نہیں" in text(bridge)
          and "انڈونیشی متبادل متن وی ایہہ وادھو سرخی دسدا اے" in text(bridge))
    check("both_source_correction_records_retained", [(item["id"], item["source_key"]) for item in translation["source_corrections"]]
          == [("A10-ALT-001", "fs-id1170655200451/alt"), ("A10-ALT-002", NESTED_MEDIA + "/alt")])
    clone = copy.deepcopy(bridge)
    for index, (media_id, number) in enumerate((("fs-id1170655200451", "5,278,194"), (NESTED_MEDIA, "63,407,218")), 1):
        correction_id = f"a10-alt-correction-{index}"
        correction = by_id(clone, correction_id)
        check(f"correction_anchor_on_matching_original_paragraph:{correction_id}", correction.tag == "p"
              and number in text(correction) and "انڈونیشی" in text(correction))
        correction.attrib.pop("id")
        image = by_id(document, media_id)
        advisory_id = correction_id + "-advisory"
        advisory = by_id(document, advisory_id)
        links = advisory.findall("a")
        check(f"source_alt_correction_discoverable:{media_id}", image.get("aria-describedby") == advisory_id
              and advisory.get("data-origin") == "renderer-ui" and len(links) == 1
              and links[0].get("href") == "#" + correction_id
              and "ساڈی وکھری درستی تے وضاحت" in text(links[0]))
    check("original_bridge_exact_except_two_verified_presentation_anchors", signature(clone) == signature(ET.fromstring(translation["bridge_after_html"])))
    check("original_scale_examples_and_source_grouping_preserved", all(value in text(bridge) for value in
          ("1,000,000", "1,000,000,000", "1,000,000,000,000", "لکھّاں تے کروڑاں والے انداز وچ نہیں بدلیا")))
    check("natural_whole_integer_conventions_disclosed", "قدرتی عدد 1 توں شروع" in text(bridge)
          and "پورے عدداں وچ 0 وی شامل" in text(bridge) and "صحیح عدداں وچ منفی عدد" in text(bridge))
    return ["A10-ALT-001", "A10-ALT-002"]


def validate_links(document, source, manifest, check=require):
    labels = {item["figure_id"]: item["local_label"] for item in manifest["images"] if item["figure_id"]}
    check("two_explicitly_local_figure_labels", list(labels.values()) == ["A10-001.1", "A10-001.2"])
    original_parent = parents(source)
    original = [node for node in source.iter() if tag(node) == "link"]
    check("two_manifest_links_match_source", [{"parent_id": original_parent[node].get("id"), "target_id": node.get("target-id")} for node in original] == manifest["source_links"])
    expected = []
    for node in original:
        owner = original_parent[node].get("id")
        target_id = node.get("target-id")
        links = by_id(document, owner).findall("a")
        check(f"source_figure_link_target:{owner}", len(links) == 1 and links[0].get("href") == "#" + target_id)
        label = links[0].findall("bdi")
        check(f"source_figure_link_local_label:{owner}", len(label) == 1 and label[0].get("dir") == "ltr"
              and text(label[0]) == labels[target_id] and text(links[0]) == "شکل " + labels[target_id])
        check(f"source_link_marker:{owner}", links[0].get("data-source-target") == target_id)
        expected.append("#" + target_id)
    source_link_nodes = [node for node in document.iter("a") if node.get("data-source-target")]
    check("exact_two_source_links_in_order", [node.get("href") for node in source_link_nodes] == expected)
    return expected


def validate_image_bytes(actual, original, spec, check=require):
    check(f"source_image_digest:{spec['media_id']}", actual == original == spec["sha256"])


def validate_images(document, source, manifest, check=require):
    original_parent = parents(source)
    target_parent = parents(document)
    source_media = [node for node in source.iter() if tag(node) == "media"]
    images = list(document.iter("img"))
    figures = list(document.iter("figure"))
    check("three_images_two_figures_in_source_order", len(source_media) == len(images) == len(manifest["images"]) == 3
          and [node.get("id") for node in figures] == [spec["figure_id"] for spec in manifest["images"] if spec["figure_id"]])
    records = []
    for original_media, image, spec in zip(source_media, images, manifest["images"]):
        media_id = spec["media_id"]
        check(f"image_source_media_identity:{media_id}", original_media.get("id") == image.get("id") == media_id)
        original_image = next(node for node in original_media if tag(node) == "image")
        original_path = WORKSPACE / spec["canonical_local_path"]
        module_path = WORKSPACE / manifest["canonical_local_path"]
        asset_path = BASE / spec["path"]
        check(f"source_image_path_binding:{media_id}", original_image.get("src") == spec["source_src"]
              and (module_path.parent / original_image.get("src")).resolve() == original_path.resolve()
              and (READER.parent / image.get("src")).resolve() == asset_path.resolve())
        validate_image_bytes(sha256(asset_path, False), sha256(original_path, False), spec, check)
        check(f"source_image_size:{media_id}", asset_path.stat().st_size == original_path.stat().st_size == spec["bytes"])
        dimensions = jpeg_dimensions(asset_path.read_bytes())
        check(f"source_image_dimensions:{media_id}", dimensions == (spec["width"], spec["height"])
              == (int(image.get("width")), int(image.get("height"))))
        wrapper = target_parent[image]
        check(f"image_scroll_ltr_focusable:{media_id}", wrapper.get("dir") == "ltr" and wrapper.get("tabindex") == "0"
              and wrapper.get("role") == "region" and "figure-scroll" in wrapper.get("class", "").split())
        check(f"no_inline_image_mirroring:{media_id}", "transform" not in image.get("style", "") and "transform" not in wrapper.get("style", ""))
        if spec["figure_id"]:
            original_figure = original_parent[original_media]
            check(f"source_figure_identity:{media_id}", tag(original_figure) == "figure" and original_figure.get("id") == spec["figure_id"]
                  and image in list(by_id(document, spec["figure_id"]).iter()))
        else:
            check(f"unnumbered_source_media_identity:{media_id}", spec["local_label"] is None
                  and original_parent[original_media].get("id") == spec["parent_para_id"] == MIXED
                  and image in list(by_id(document, MIXED).iter()))
        records.append({"media_id": media_id, "figure_id": spec["figure_id"], "local_label": spec["local_label"],
                        "path": spec["path"], "sha256": spec["sha256"], "bytes": spec["bytes"],
                        "width": dimensions[0], "height": dimensions[1]})
    return records


def validate_directions_and_local_links(document, check=require):
    parent = parents(document)

    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = parent.get(node)
        return None

    check("all_bdi_explicitly_ltr", all(node.get("dir") == "ltr" for node in document.iter("bdi")))
    check("all_english_language_lanes_ltr", all(direction(node) == "ltr" for node in document.iter() if node.get("lang") == "en"))
    for node in document.find("body").iter():
        for fragment in [node.text or "", *[child.tail or "" for child in node]]:
            if re.search(r"[A-Za-z0-9]", fragment):
                require("visible_latin_and_numbers_in_ltr_lanes", direction(node) == "ltr")
    check("visible_latin_and_numbers_in_ltr_lanes", True)
    local = []
    for node in document.iter():
        for attribute in ("href", "src", "aria-describedby"):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
            if attribute == "aria-describedby":
                for identifier in value.split():
                    by_id(document, identifier)
                continue
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
    check("all_local_file_fragment_and_description_targets_resolve", True)
    return local


def validate_mutations(document, source, translation, manifest, check=require):
    names = []

    def reject(name, mutate, validate, prefix):
        mutant = copy.deepcopy(document)
        mutate(mutant)
        try:
            validate(mutant)
        except AssertionError as error:
            check(name, str(error).startswith(prefix))
            names.append(name)
        else:
            raise AssertionError(name + ":mutation_not_rejected")

    def change_question_digit(mutant):
        question = by_id(mutant, "fs-id1166421427575").find("li")
        labels = question.findall("bdi")
        labels[1].text = "8"

    def change_answer_position(mutant):
        answer = by_id(mutant, "fs-id1170655163552")
        label = next(answer.iter("bdi"))
        label.tail = label.tail.replace("بلیناں", "ملیناں")

    def swap_term_ids(mutant):
        first = by_id(mutant, "term-00001")
        second = by_id(mutant, "term-00002")
        first.set("id", "term-00002")
        second.set("id", "term-00001")

    def move_media_out_of_paragraph(mutant):
        mixed = by_id(mutant, MIXED)
        media = by_id(mutant, NESTED_MEDIA)
        wrapper = next(node for node in mixed if media in list(node.iter()))
        mixed.remove(wrapper)
        parents(mutant)[mixed].append(wrapper)

    def move_newline_after_media(mutant):
        mixed = by_id(mutant, MIXED)
        newline = mixed.find("br")
        mixed.remove(newline)
        mixed.append(newline)

    def duplicate_solution_heading(mutant):
        solution = by_id(mutant, "fs-id1170655022351")
        solution.insert(0, copy.deepcopy(solution.find("h3")))

    def split_answer_outside_wrapper(mutant):
        wrapper = by_id(mutant, "fs-id1170654924451").findall("span")[2]
        child = wrapper[-1]
        offset = child.tail.index("ہزار")
        wrapper.tail = child.tail[offset:] + (wrapper.tail or "")
        child.tail = child.tail[:offset]

    reject("mutation_question_digit_rejected", change_question_digit,
           lambda doc: validate_answers(doc, source), "rendered_question_digit:")
    reject("mutation_answer_place_rejected", change_answer_position,
           lambda doc: validate_answers(doc, source), "answer_position_source_exact:")
    reject("mutation_source_number_grouping_rejected", lambda doc: setattr(by_id(doc, "fs-id1170655192807").find("bdi"), "text", "6,34,07,218"),
           lambda doc: validate_answers(doc, source), "exercise_source_number:")
    reject("mutation_source_alt_error_erasure_rejected", lambda doc: by_id(doc, "fs-id1170655200451").set("alt", by_id(doc, "fs-id1170655200451").get("alt").replace("دو سو اُناسی ہزار", "دو سو اَٹھہتر ہزار")),
           lambda doc: validate_source_discrepancies(doc, source, translation), "source_number_name_error_retained_in_translated_alt")
    reject("mutation_source_title_row_claim_erasure_rejected", lambda doc: by_id(doc, NESTED_MEDIA).set("alt", by_id(doc, NESTED_MEDIA).get("alt").replace("جدول دی اُتلی سرخی «جگہ دی قدر» اے", "جدول دی کوئی وکھری اُتلی سرخی نہیں")),
           lambda doc: validate_source_discrepancies(doc, source, translation), "source_absent_title_row_claim_retained_in_alt")
    reject("mutation_image_path_swap_rejected", lambda doc: by_id(doc, manifest["images"][0]["media_id"]).set("src", "../" + manifest["images"][1]["path"]),
           lambda doc: validate_images(doc, source, manifest), "source_image_path_binding:")
    reject("mutation_source_figure_link_rejected", lambda doc: by_id(doc, "fs-id1170655197123").find("a").set("href", "#" + manifest["images"][1]["figure_id"]),
           lambda doc: validate_links(doc, source, manifest), "source_figure_link_target:")
    reject("mutation_term_order_rejected", swap_term_ids,
           lambda doc: validate_structure(doc, source, manifest), "all_43_source_ids_in_exact_order")
    reject("mutation_part_order_rejected", lambda doc: setattr(by_id(doc, "fs-id1166421427575").find("li/bdi"), "text", "(b)"),
           lambda doc: validate_parts(doc, source), "all_30_parts_in_exact_order")
    reject("mutation_media_moved_out_of_source_paragraph_rejected", move_media_out_of_paragraph,
           lambda doc: validate_mixed_and_newlines(doc, source), "mixed_paragraph_valid_block_container")
    reject("mutation_invalid_mixed_paragraph_tag_rejected", lambda doc: setattr(by_id(doc, MIXED), "tag", "p"),
           lambda doc: validate_mixed_and_newlines(doc, source), "mixed_paragraph_valid_block_container")
    reject("mutation_newline_moved_after_media_rejected", move_newline_after_media,
           lambda doc: validate_mixed_and_newlines(doc, source), "newline_precedes_nested_media_once")
    reject("mutation_explicit_solution_heading_duplicated_rejected", duplicate_solution_heading,
           lambda doc: validate_structure(doc, source, manifest), "explicit_source_solution_title_once")
    reject("mutation_alt_advisory_targets_wrong_correction_rejected", lambda doc: by_id(doc, "a10-alt-correction-1-advisory").find("a").set("href", "#a10-alt-correction-2"),
           lambda doc: validate_source_discrepancies(doc, source, translation), "source_alt_correction_discoverable:")
    reject("mutation_part_answer_split_outside_wrapper_rejected", split_answer_outside_wrapper,
           lambda doc: validate_inline_part_groups(doc, source, translation), "complete_part_inside_wrapper:")
    reject("mutation_part_wrapper_identity_changed_rejected", lambda doc: by_id(doc, "fs-id1170654924451").find("span").set("data-source-part", "e"),
           lambda doc: validate_inline_part_groups(doc, source, translation), "source_part_wrapper_identity:")
    reject("mutation_math_spacing_changed_rejected", lambda doc: next(doc.iter("{" + MATH + "}mspace")).set("width", "2em"),
           lambda doc: validate_math(doc, source), "math_tree_exact_without_any_text_edit:")
    reject("mutation_math_wrapper_text_rejected", lambda doc: setattr(next(doc.iter("{" + MATH + "}math")), "tail", "=999"),
           lambda doc: validate_math(doc, source), "pure_ltr_math_wrapper:")
    spec = manifest["images"][0]
    altered = ("0" if spec["sha256"][0] != "0" else "1") + spec["sha256"][1:]
    try:
        validate_image_bytes(altered, spec["sha256"], spec)
    except AssertionError as error:
        name = "mutation_image_digest_rejected_without_asset_write"
        check(name, str(error) == "source_image_digest:" + spec["media_id"])
        names.append(name)
    else:
        raise AssertionError("mutated_image_digest_not_rejected")
    return names


def validate_existing_attribution(document, manifest, check=require):
    retained = []
    for item in manifest["existing_notice_inputs"]:
        path = WORKSPACE / item["path"]
        check(f"existing_notice_hash_retained:{path.name}", hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == item["sha256"])
        retained.append({"path": item["path"], "sha256": item["sha256"]})
    footers = document.findall(".//footer")
    check("one_a10_attribution_footer", len(footers) == 1)
    footer = footers[0]
    value = text(footer)
    check("a10_book_and_senior_contributors_retained", "Elementary Algebra 2e" in value
          and all(name in value for name in ("Lynn Marecek", "MaryAnne Anthony-Smith", "Andrea Honeycutt Mathis")))
    check("no_a30_credits_substituted", not any(name in value for name in ("Jay Abramson", "David Lippman", "Melonie Rasmussen", "Precalculus 2e", "m49301")))
    links = [node.get("href") for node in footer.iter("a")]
    canonical_url = manifest["upstream_url"] + "/blob/" + manifest["commit"] + "/" + manifest["path"]
    check("attribution_targets_exact_canonical_module", canonical_url in links)
    check("existing_book_license_link_retained", "https://creativecommons.org/licenses/by-nc-sa/4.0/" in links)
    check("existing_notice_and_license_files_linked", any(href.endswith("A10-release/NOTICE.txt") for href in links)
          and any(href.endswith("upstream--osbooks-prealgebra-bundle/LICENSE") or href.endswith("A10-release/LICENSE.txt") for href in links))
    check("nonendorsement_retained", "OpenStax" in value and "Rice University" in value and "do not endorse" in value)
    check("a10_footer_english_ltr", footer.get("lang") == "en" and footer.get("dir") == "ltr")
    return retained


def validate_component_notices(notices, manifest, check=require):
    check("component_evidence_schema_and_scope", notices["schema"] == "a10-retained-component-evidence-v1"
          and notices["unit"] == "A10-001" and notices["module"] == "m82452" and notices["collection"] == "col31130"
          and notices["commit"] == manifest["commit"] and notices["work"] == "OpenStax Elementary Algebra 2e")
    check("component_evidence_manifest_and_excerpt_hashes", notices["manifest_sha256"] == sha256(MANIFEST, False)
          and notices["excerpt_sha256"] == manifest["excerpt_sha256"])
    check("component_evidence_existing_inputs_exact", notices["existing_notice_inputs"] == manifest["existing_notice_inputs"])
    release_notice = BASE / "provenance/A10-release/NOTICE.txt"
    check("existing_release_notice_retained_verbatim", notices["release_notice_verbatim"] == release_notice.read_text(encoding="utf-8"))
    check("existing_license_statement_retained", notices["existing_license_statement"] in notices["release_notice_verbatim"])
    check("no_new_component_clearance_claim", "no new component-specific clearance determination" in notices["rights_status"]
          and "not rights holders or permissions" in notices["credit_limit"]
          and "not clearance" in notices["credit_limit"])
    media_manifest = WORKSPACE / notices["media_authority_manifest"]["path"]
    check("existing_media_authority_manifest_hash", sha256(media_manifest, False) == notices["media_authority_manifest"]["sha256"])
    with media_manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    records = notices["images"]
    check("three_component_records_in_source_order", len(records) == 3
          and [item["media_id"] for item in records] == [item["media_id"] for item in manifest["images"]])
    for item, spec in zip(records, manifest["images"]):
        media_id = spec["media_id"]
        keys = ("figure_id", "media_id", "source_path", "path", "sha256", "bytes", "width", "height")
        check(f"component_identity_and_dimensions:{media_id}", all(item[key] == spec[key] for key in keys))
        matched = [row for row in rows if row["relative_path"] == spec["source_path"]]
        check(f"existing_media_authority_row_retained:{media_id}", len(matched) == 1 and item["existing_media_authority_row"] == matched[0])
        actual = (BASE / spec["path"]).read_bytes()
        row = item["existing_media_authority_row"]
        check(f"reader_image_matches_existing_authority_blob:{media_id}", len(actual) == int(row["bytes"])
              and hashlib.sha256(actual).hexdigest() == row["sha256"]
              and hashlib.sha1(b"blob " + str(len(actual)).encode() + b"\0" + actual).hexdigest() == row["git_blob_sha1"])
        check(f"component_no_new_clearance:{media_id}", item["component_clearance"] == "Not newly assessed; subject to retained component-specific credits and restrictions.")
    check("notice_does_not_claim_book_completion", notices["whole_book_translation_complete"] is False
          and notices["earlier_collection_items_pending"] == manifest["earlier_collection_items_still_pending"])
    return {"record": NOTICES.relative_to(BASE).as_posix(), "sha256": sha256(NOTICES, False),
            "rights_scope": "Existing audited policy retained; identity checks are not new component clearance"}


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    translation = json.loads(TRANSLATION.read_text(encoding="utf-8"))
    notices = json.loads(NOTICES.read_text(encoding="utf-8"))
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    inputs = [MANIFEST, TRANSLATION, excerpt, NOTICES, BASE / "scripts/prepare_a10.py", BASE / "scripts/build_a10.py",
              BASE / "scripts/qa_notation.py", Path(__file__).resolve(), BASE / "styles/reader.css", BASE / "sources.lock.json",
              BASE / "qa/a10-unit-001-language-notes.md", BASE / "canon/examples.json",
              *[WORKSPACE / item["path"] for item in manifest["existing_notice_inputs"]],
              *[BASE / item["path"] for item in manifest["images"]]]
    initial = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    command = [sys.executable, str(BASE / "scripts/build_a10.py")]
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

    check("frozen_excerpt_sha256", sha256(excerpt) == manifest["excerpt_sha256"])
    check("frozen_excerpt_lf_byte_size", len(excerpt.read_bytes().replace(b"\r\n", b"\n")) == manifest["excerpt_bytes"])
    check("exact_a10_locale_and_scope", manifest["locale"] == translation["locale"] == document.get("lang") == "pnb-Arab-PK"
          and document.get("dir") == "rtl" and manifest["unit"] == translation["unit"] == "A10-001"
          and manifest["assignment"] == translation["assignment"] == "A10")
    check("a10_reader_header_metadata", text(document.find("head/title")) == translation["title"] + " — A10-001"
          and document.find("body").get("class") == "a10-reader")
    check("pending_collection_work_and_five_work_scope_visible", "پورا سبق یا پوری کتاب نہیں" in raw
          and "m82630" in raw and "m82451" in raw and "پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے" in raw)
    for path in [*inputs, READER]:
        if path.suffix != ".jpg":
            check(f"unicode_clean:{path.relative_to(BASE).as_posix()}", not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", raw))
    counts = validate_source(source, manifest, check)
    source_ids = validate_structure(document, source, manifest, check)
    newlines = validate_mixed_and_newlines(document, source, check)
    specs, numerals = validate_blocks(document, source, translation, manifest, check)
    mathematics = validate_math(document, source, check)
    source_parts = validate_parts(document, source, check)
    inline_groups = validate_inline_part_groups(document, source, translation, check)
    answers = validate_answers(document, source, check)
    discrepancies = validate_source_discrepancies(document, source, translation, check)
    links = validate_links(document, source, manifest, check)
    images = validate_images(document, source, manifest, check)
    local = validate_directions_and_local_links(document, check)
    retained = validate_existing_attribution(document, manifest, check)
    components = validate_component_notices(notices, manifest, check)
    mutations = validate_mutations(document, source, translation, manifest, check)
    check("detached_mutations_leave_reader_unchanged", first == READER.read_bytes())
    final = {path.relative_to(BASE).as_posix(): sha256(path) for path in inputs}
    check("checked_inputs_stable_during_run", initial == final)
    final[READER.relative_to(BASE).as_posix()] = sha256(READER, False)
    receipt = {
        "unit": "A10-001", "status": "structural_pass_linguistic_and_visual_review_separate",
        "translated_blocks": len(specs), "source_block_keys": list(specs), "source_ids_preserved": len(source_ids), "source_ids": source_ids,
        "source_counts": counts, "math": mathematics, "source_prose_and_alt_numerals": numerals,
        "source_newlines": newlines, "source_part_labels": source_parts, "question_answer_mathematics": answers,
        "source_inline_part_groups": inline_groups,
        "images": images, "source_links": links, "disclosed_source_discrepancies": discrepancies,
        "retained_notice_inputs": retained, "components": components, "local_reference_count": len(local),
        "detached_mutations": mutations, "checks": checks, "hashes": final,
        "canon_consultation": {"examples": ["C01", "C03", "C04", "C07", "C10"],
            "method": "Actual local R1/R2/R3 prose loci read during QA implementation; automated runs do not claim a fresh reading",
            "application": "Punjabi ability, ordered description, number/plural agreement, position language and separately labeled qualifications checked; provisional terminology remains uncertified."},
        "limitations": [
            "Only the declared opening selection is covered; earlier collection items, the rest of m82452, all A10 and the five-work assignment remain incomplete.",
            "Exact string/ID checks and a small explicit Punjabi place-name map do not certify native-language naturalness, all number words or educator approval.",
            "The two MathML trees carry spacing only. The 15 digit-place answers and comma-grouped numerals are checked separately from those trees.",
            "Source-image hashes and dimensions bind the original pixels; the original images were viewed during implementation, but the automated script does not interpret raster labels.",
            "Both known alt errors are deliberately retained and linked to original correction notes. aria-describedby/link presence is checked, not screen-reader pronunciation or practical discoverability.",
            "HTML void elements are self-closed in an in-memory XML inspection copy; no DOM nesting repairs are made. Browser layout, bidi shaping, keyboard interaction, viewport overflow and font portability need separate visual/accessibility checks.",
            "Mobile part grouping is checked as 25 exact source-derived presentation spans; only verified wrappers are removed in memory for exact markup/text/whitespace comparison. Actual wrapping and short-answer fit still require visual inspection.",
            "The retained component record supplies existing identity and notice evidence, not a new license/supply audit or image-specific clearance.",
            "External URL availability is not network-tested. No original source, image or translation is modified by detached mutation tests.",
        ],
    }
    (BASE / "qa/structural-a10-001.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(checks)} checks; 30 source blocks; 43 source IDs; 15 question-answer pairs; 3 original images; {len(mutations)} detached mutations")


if __name__ == "__main__":
    main()
