"""Source-bound structural and reversible-MathML QA for PNB-004.

Only deterministic reader builds and the generated QA receipt are written.
All adversarial tests mutate detached DOMs, not manuscripts or source assets.
"""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
import copy
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
READER = BASE / "reader/unit-004.html"
MANIFEST = BASE / "source-excerpts/manifest-004.json"
TRANSLATION = BASE / "translations/unit-004.json"
NOTICES = BASE / "provenance/unit-004-component-notices.json"
MATH = "http://www.w3.org/1998/Math/MathML"
LEDGER = "data-source-text-edits"
FORBIDDEN = re.compile(r"[\u0a00-\u0a7f\ufffd\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]")


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def sha256(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def text(node):
    return "".join(node.itertext()).strip()


def parse_reader(data):
    return ET.fromstring(data[data.index("<html"):])


def by_id(document, identifier):
    nodes = [node for node in document.iter() if node.get("id") == identifier]
    require(f"one_source_id:{identifier}", len(nodes) == 1)
    return nodes[0]


def paths(node, path=()):
    yield path, node
    for index, child in enumerate(node):
        yield from paths(child, path + (index,))


def at_path(node, path):
    for index in path:
        require("ledger_path_in_bounds", type(index) is int and 0 <= index < len(node))
        node = node[index]
    return node


def allowed_punctuation_edits(source_math):
    """Independent positional policy on the original source, never ledger.old.

    Whole English mtext sentences, spaces/NBSP, parentheses and internal commas
    are not strip/rstrip targets. A combined terminal '),' keeps its parenthesis.
    """
    leaves = [(path, node) for path, node in paths(source_math) if not len(node)]
    allowed = {}
    if leaves:
        first_path, first = leaves[0]
        if tag(first) in ("mo", "mtext") and first.text in ("“", "”"):
            allowed[first_path] = (first.text, "")
    suffix = len(leaves)
    while suffix:
        path, leaf = leaves[suffix - 1]
        if tag(leaf) in ("mo", "mtext") and leaf.text in (".", ",", "“", "”"):
            allowed[path] = (leaf.text, "")
            suffix -= 1
            continue
        if tag(leaf) == "mo" and leaf.text == "),":
            allowed[path] = ("),", ")")
        break
    return allowed


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require("ledger_json_keys_unique", key not in result)
        result[key] = value
    return result


def signature(node):
    """Exact expanded tags/attributes/text and child tails; root tail is prose."""
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((signature(child), child.tail) for child in node))


def restore_math(source_math, target_math, ordinal):
    require(f"math_root_ltr:{ordinal}", target_math.get("dir") == "ltr")
    require(f"no_source_presentation_metadata:{ordinal}", "dir" not in source_math.attrib
            and LEDGER not in source_math.attrib)
    raw = target_math.get(LEDGER)
    try:
        entries = [] if raw is None else json.loads(raw, object_pairs_hook=unique_object)
    except (ValueError, TypeError) as error:
        raise AssertionError(f"ledger_valid_json:{ordinal}") from error
    require(f"ledger_is_list:{ordinal}", isinstance(entries, list))
    require(f"ledger_not_empty_if_present:{ordinal}", raw is None or bool(entries))
    allowed = allowed_punctuation_edits(source_math)
    restored = copy.deepcopy(target_math)
    seen = set()
    for entry in entries:
        require(f"ledger_exact_schema:{ordinal}", isinstance(entry, dict)
                and set(entry) == {"path", "old", "new"}
                and isinstance(entry["path"], list)
                and all(type(index) is int and index >= 0 for index in entry["path"])
                and isinstance(entry["old"], str) and isinstance(entry["new"], str))
        path = tuple(entry["path"])
        require(f"ledger_paths_unique:{ordinal}", path not in seen)
        seen.add(path)
        require(f"punctuation_edit_position_whitelisted:{ordinal}", path in allowed)
        original_leaf = at_path(source_math, path)
        target_leaf = at_path(restored, path)
        old, new = allowed[path]
        require(f"ledger_old_matches_source:{ordinal}", entry["old"] == old == original_leaf.text)
        require(f"ledger_new_matches_policy:{ordinal}", entry["new"] == new)
        # XML parsing turns explicitly cleared text into None; this equivalence
        # is permitted only here, for an independently whitelisted edit.
        require(f"ledger_new_matches_rendered_text:{ordinal}",
                target_leaf.text == new or (new == "" and target_leaf.text is None))
        require(f"edited_node_topology_unchanged:{ordinal}", len(target_leaf) == len(original_leaf) == 0
                and target_leaf.tag == original_leaf.tag)
        target_leaf.text = original_leaf.text
    require(f"complete_expected_punctuation_ledger:{ordinal}", seen == set(allowed))
    restored.attrib.pop("dir")
    restored.attrib.pop(LEDGER, None)
    require(f"math_tree_exactly_reconstructed:{ordinal}", signature(restored) == signature(source_math))
    return len(entries)


def nearest_source_owner(node, parents, source_ids):
    while node in parents:
        node = parents[node]
        if node.get("id") in source_ids:
            return node.get("id")
    raise AssertionError("math_has_source_id_owner")


def validate_math(document, source):
    originals = list(source.iter("{" + MATH + "}math"))
    rendered = [node for node in document.iter() if tag(node) == "math"]
    require("math_tree_count_and_namespace", len(rendered) == len(originals) == 46
            and all(node.tag == "{" + MATH + "}math" for node in rendered))
    original_parents = {child: parent for parent in source.iter() for child in parent}
    rendered_parents = {child: parent for parent in document.iter() for child in parent}
    ids = {node.get("id") for node in source.iter() if node is not source and node.get("id")}
    original_owners = [nearest_source_owner(node, original_parents, ids) for node in originals]
    target_owners = [nearest_source_owner(node, rendered_parents, ids) for node in rendered]
    require("math_source_owner_and_per_owner_order", target_owners == original_owners)
    require("all_math_isolated_ltr", all(rendered_parents[node].tag == "span"
            and rendered_parents[node].get("class") == "math-isolate"
            and rendered_parents[node].get("dir") == "ltr" for node in rendered))
    require("math_wrappers_contain_only_their_math", all(
        len(rendered_parents[node]) == 1 and rendered_parents[node][0] is node
        and rendered_parents[node].text in (None, "") and node.tail in (None, "")
        for node in rendered
    ))
    for equation in (node for node in source.iter() if tag(node) == "equation"):
        displayed = by_id(document, equation.get("id"))
        expected_count = sum(tag(child) == "math" for child in equation)
        require("source_equation_contains_only_expected_math_wrappers",
                displayed.text in (None, "") and len(displayed) == expected_count
                and all(child in rendered_parents.values() and child.tag == "span"
                        and child.get("class") == "math-isolate" and child.tail in (None, "")
                        for child in displayed))
    require("ledgers_only_on_math_roots", all(node in rendered for node in document.iter() if LEDGER in node.attrib))
    counts = [restore_math(original, target, ordinal) for ordinal, (original, target)
              in enumerate(zip(originals, rendered))]
    # Even a non-punctuation mtext change supplied with a forged reversible
    # ledger cannot evade the source-position policy and exact restoration.
    english_mtext = 0
    for original, target in zip(originals, rendered):
        for path, node in paths(original):
            if tag(node) == "mtext" and re.search(r"[A-Za-z]", node.text or ""):
                require("english_mtext_text_and_nbsp_retained", at_path(target, path).text == node.text)
                english_mtext += 1
    return {"trees": len(originals), "edited_trees": sum(bool(count) for count in counts),
            "text_edits": sum(counts), "english_mtext_nodes": english_mtext,
            "source_owners_in_tree_order": original_owners}


def prose(node):
    """Skip MathML while retaining its tail, which belongs to source prose."""
    pieces = [node.text or ""]
    for child in node:
        if tag(child) != "math":
            pieces.append(prose(child))
        pieces.append(child.tail or "")
    return "".join(pieces)


def validate_source_text(document, source, translation):
    parents = {child: parent for parent in source.iter() for child in parent}
    expected_keys = []
    numeral_receipt = {}
    for node in source.iter():
        name = tag(node)
        if name not in ("title", "label", "para", "media"):
            continue
        if name == "label" and not text(node):
            continue
        parent = parents[node]
        key = node.get("id") or f"{parent.get('id')}/{name}"
        if name == "media":
            key += "/alt"
            original_prose = node.get("alt", "")
            rendered_prose = by_id(document, node.get("id")).get("alt", "")
            target_prose = translation["source_blocks"][key]
        else:
            original_prose = prose(node)
            if node.get("id"):
                rendered_node = by_id(document, node.get("id"))
            else:
                heading = "h2" if name == "title" and tag(parent) == "section" else "h3"
                headings = by_id(document, parent.get("id")).findall(heading)
                require(f"one_translated_heading:{key}", len(headings) == 1)
                rendered_node = headings[0]
            rendered_prose = prose(rendered_node)
            fragment = re.sub(r"\{\{math:\d+\}\}", "", translation["source_blocks"][key])
            target_prose = prose(ET.fromstring("<fragment>" + fragment + "</fragment>"))
        require(f"translated_prose_bound_to_source_key:{key}", rendered_prose == target_prose)
        original_numbers = re.findall(r"\d+", original_prose)
        require(f"source_prose_numerals_preserved:{key}", re.findall(r"\d+", rendered_prose) == original_numbers)
        if original_numbers:
            numeral_receipt[key] = original_numbers
        expected_keys.append(key)
    require("all_23_source_text_keys_exact", len(expected_keys) == len(translation["source_blocks"]) == 23
            and set(expected_keys) == set(translation["source_blocks"]))
    return numeral_receipt


def validate_hierarchy(document, source):
    ids = [node.get("id") for node in document.iter() if node.get("id")]
    original_ids = [node.get("id") for node in source.iter() if node is not source and node.get("id")]
    require("unique_html_ids", len(ids) == len(set(ids)))
    require("all_35_source_ids_in_order", len(original_ids) == 35
            and [identifier for identifier in ids if identifier in original_ids] == original_ids)
    require("excerpt_root_not_rendered", source.get("id") not in ids)
    original_parents = {child: parent for parent in source.iter() for child in parent}
    rendered_parents = {child: parent for parent in document.iter() for child in parent}

    def chain(node, parents):
        result = []
        while node in parents:
            node = parents[node]
            if node.get("id") in original_ids:
                result.append(node.get("id"))
        return result

    require("source_id_ancestor_chains_exact", all(
        chain(node, original_parents) == chain(by_id(document, node.get("id")), rendered_parents)
        for node in source.iter() if node is not source and node.get("id")
    ))
    return original_ids


def validate_bilingual_key(document, source):
    bridge = by_id(document, "notation-bridge")
    require("notation_bridge_marked_original", bridge.get("data-origin") == "original-bridge"
            and re.search(r"[\u0600-\u06ff]", text(bridge)) is not None)
    displays = [node for node in source.iter("{" + MATH + "}math") if node.get("display") == "block"]
    require("one_source_display_equation", len(displays) == 1)
    rows = [node for node in displays[0].iter() if tag(node) == "mtr"]
    key_rows = bridge.findall("./ol/li")
    require("all_display_rows_have_bilingual_explanation", len(rows) == len(key_rows))
    for row, key in zip(rows, key_rows):
        first_cell = next(node for node in row if tag(node) == "mtd")
        first_label = key.find("bdi")
        require("display_row_expression_key_matches_source", first_label is not None
                and re.sub(r"\s", "", text(first_label)) == re.sub(r"\s", "", text(first_cell))
                and re.search(r"[\u0600-\u06ff]", text(key)) is not None)
    inline_words = []
    for math in source.iter("{" + MATH + "}math"):
        if math.get("display") == "block":
            continue
        inline_words.extend(text(node) for node in math.iter() if tag(node) == "mtext"
                            and re.fullmatch(r"[A-Za-z]+", text(node)))
    media = next(node for node in source.iter() if tag(node) == "media")
    image_expression = re.search(r"\bfunction (\d+\s*=\s*[A-Za-z]\(([^)]+)\))", media.get("alt", ""))
    require("source_image_expression_parsed", image_expression is not None)
    diagram_words = [image_expression[2], *re.findall(r"is the ([a-z]+)", media.get("alt", ""))]
    key_labels = [text(node) for node in bridge.iter("bdi") if node.get("lang") == "en"]
    require("inline_and_diagram_english_words_have_key", all(word in key_labels for word in inline_words + diagram_words))
    image_expression_text = re.sub(r"\s", "", image_expression[1])
    require("january_diagram_expression_retained_in_key_and_alt", any(
        re.sub(r"\s", "", text(node)) == image_expression_text for node in bridge.iter("bdi")
    ) and image_expression_text in re.sub(r"\s", "", by_id(document, media.get("id")).get("alt", "")))
    return list(dict.fromkeys(inline_words + diagram_words))


def validate_directions_and_links(document):
    parents = {child: parent for parent in document.iter() for child in parent}

    def direction(node):
        while node is not None:
            if node.get("dir"):
                return node.get("dir")
            node = parents.get(node)
        return None

    require("all_bdi_ltr", all(node.get("dir") == "ltr" for node in document.iter("bdi")))
    require("english_lanes_ltr", all(direction(node) == "ltr" for node in document.iter() if node.get("lang") == "en"))
    for node in document.find("body").iter():
        for value in [node.text or "", *[child.tail or "" for child in node]]:
            if re.search(r"[A-Za-z0-9]", value):
                require("visible_latin_and_numbers_ltr", direction(node) == "ltr")
    local = []
    for node in document.iter():
        for attribute in ("href", "src"):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
            parsed = urlsplit(value)
            if parsed.scheme in ("http", "https", "mailto"):
                continue
            require("supported_local_url", not parsed.scheme and not parsed.netloc)
            target = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            require(f"local_file_resolves:{value}", target.is_file())
            if parsed.fragment:
                linked = document if target == READER.resolve() else parse_reader(target.read_text(encoding="utf-8"))
                by_id(linked, unquote(parsed.fragment))
            local.append(value)
    require("previous_unit_navigation", any(node.get("href") == "unit-003.html" for node in document.findall(".//nav/a")))
    return local


def jpeg_dimensions(data):
    require("jpeg_start", data[:2] == b"\xff\xd8")
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset < len(data):
        require("jpeg_marker", data[offset] == 0xFF)
        while data[offset] == 0xFF:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], "big")
        require("jpeg_segment_bounds", length >= 2 and offset + length <= len(data))
        if marker in sof:
            return (int.from_bytes(data[offset + 5:offset + 7], "big"),
                    int.from_bytes(data[offset + 3:offset + 5], "big"))
        require("jpeg_dimensions_before_scan", marker != 0xDA)
        offset += length
    raise AssertionError("jpeg_dimensions_present")


def validate_image_digest(actual, original, spec, notice):
    require("original_image_digest_agreement", actual == original == spec["sha256"] == notice["sha256"])


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    notices = json.loads(NOTICES.read_text(encoding="utf-8"))
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    input_paths = [TRANSLATION, MANIFEST, excerpt, NOTICES, BASE / "styles/reader.css",
                   BASE / "terminology.tsv", BASE / "scripts/build.py", Path(__file__).resolve(),
                   BASE / "provenance/ATTRIBUTION.md", *[BASE / spec["path"] for spec in manifest["images"]]]
    initial_hashes = {path.relative_to(BASE).as_posix(): sha256(path) for path in input_paths}
    command = [sys.executable, str(BASE / "scripts/build.py"), "--unit", "004"]
    subprocess.run(command, check=True)
    first = READER.read_bytes()
    subprocess.run(command, check=True)
    require("deterministic_build", READER.read_bytes() == first)
    raw = first.decode("utf-8")
    document = parse_reader(raw)
    translation = json.loads(TRANSLATION.read_text(encoding="utf-8"))
    checks = ["deterministic_build"]

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    check("frozen_quote_and_math_witness_hash", sha256(excerpt) == manifest["excerpt_sha256"])
    check("exact_locale_rtl_and_unit", document.get("lang") == translation["locale"] == "pnb-Arab-PK"
          and document.get("dir") == "rtl" and translation["unit"] == manifest["unit"] == "PNB-004")
    check("exact_selected_section", [node.get("id") for node in source] == manifest["selection_ids"] == ["fs-id1165134474160"]
          and manifest["next_source_id"] == "fs-id1165137804204")
    for path in [*input_paths, READER]:
        if path.suffix != ".jpg":
            check(f"unicode_clean:{path.relative_to(BASE).as_posix()}", not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", raw))
    identifiers = validate_hierarchy(document, source)
    checks.extend(["unique_ids_and_all_35_source_ids_in_order", "source_id_ancestor_hierarchy_preserved"])
    math_report = validate_math(document, source)
    checks.extend(["all_46_math_trees_bound_to_source_owners", "all_math_ltr_isolated",
                   "pure_math_wrappers_and_source_equation_container",
                   "strict_punctuation_ledger_schema_and_source_position_whitelist",
                   "complete_ledgers_restore_exact_math_tree_text_attributes_tails",
                   "all_nonpunctuation_english_mtext_retained"])
    numerals = validate_source_text(document, source, translation)
    checks.extend(["all_23_translated_text_blocks_bound_to_source_ids", "source_prose_and_alt_numerals_preserved"])
    key_words = validate_bilingual_key(document, source)
    checks.extend(["original_bilingual_key_for_every_display_row", "inline_english_and_diagram_words_have_key",
                   "distinct_january_image_and_march_prose_retained"])
    local = validate_directions_and_links(document)
    checks.extend(["latin_text_numbers_and_bdi_ltr", "local_files_fragments_and_previous_unit_navigation_resolve"])
    check("source_has_no_links_or_footnotes", not any(tag(node) in ("link", "footnote") for node in source.iter()))
    selected = by_id(document, manifest["selection_ids"][0])
    check("no_invented_source_fragment_links", not any(node.get("href", "").startswith("#") for node in selected.iter("a")))
    check("bounded_translation_disclosure", "پورے حصے دا ترجمہ نہیں" in raw)

    figures = [node for node in source.iter() if tag(node) == "figure"]
    check("one_declared_source_image", len(figures) == len(manifest["images"]) == len(notices) == len(list(document.iter("img"))) == 1)
    figure, spec, notice = figures[0], manifest["images"][0], notices[0]
    media = next(node for node in figure if tag(node) == "media")
    image = next(node for node in media if tag(node) == "image")
    rendered_figure = by_id(document, figure.get("id"))
    rendered_images = list(rendered_figure.iter("img"))
    check("source_figure_and_media_identity", figure.get("id") == spec["figure_id"]
          and len(rendered_images) == 1 and rendered_images[0].get("id") == media.get("id"))
    rendered_image = rendered_images[0]
    asset = BASE / spec["path"]
    repo = manifest["upstream_url"].rstrip("/").rsplit("/", 1)[-1]
    original = WORKSPACE / "downloads/complete-upstream" / repo / spec["source_path"]
    check("source_image_and_notice_path_binding", PurePosixPath(image.get("src")).name == PurePosixPath(spec["source_path"]).name
          and notice["asset_path"] == spec["source_path"]
          and (READER.parent / rendered_image.get("src")).resolve() == asset.resolve())
    image_digest = sha256(asset)
    validate_image_digest(image_digest, sha256(original), spec, notice)
    checks.append("source_copy_manifest_and_retained_notice_image_sha256_match")
    dimensions = jpeg_dimensions(asset.read_bytes())
    check("original_image_dimensions_and_size", dimensions == (spec["width"], spec["height"])
          == (int(rendered_image.get("width")), int(rendered_image.get("height")))
          and asset.stat().st_size == int(notice["bytes"]))

    def reject(name, operation, expected_prefix):
        try:
            operation()
        except AssertionError as error:
            check(name, str(error).startswith(expected_prefix))
        else:
            raise AssertionError(name + ":not_rejected")

    original_maths = list(source.iter("{" + MATH + "}math"))
    number_mutant = copy.deepcopy(document)
    number = next(node for node in number_mutant.iter("{" + MATH + "}mn") if (node.text or "").isdigit())
    number.text = str(int(number.text) + 1)
    reject("mutation_changed_math_number_rejected", lambda: validate_math(number_mutant, source), "math_tree_exactly_reconstructed:")

    wrapper_mutant = copy.deepcopy(document)
    display_math = next(node for node in wrapper_mutant.iter("{" + MATH + "}math") if node.get("display") == "block")
    display_math.tail = "=999"
    reject("mutation_extra_visible_display_tail_rejected", lambda: validate_math(wrapper_mutant, source),
           "math_wrappers_contain_only_their_math")

    ledger_mutant = copy.deepcopy(document)
    edited = next(node for node in ledger_mutant.iter("{" + MATH + "}math") if node.get(LEDGER))
    ledger = json.loads(edited.get(LEDGER))
    ledger[0]["old"] += "x"
    edited.set(LEDGER, json.dumps(ledger, ensure_ascii=False))
    reject("mutation_falsified_old_text_ledger_rejected", lambda: validate_math(ledger_mutant, source), "ledger_old_matches_source:")

    # Truthfully reversible internal-comma deletion must still be rejected by
    # the independent position whitelist, not accepted merely by restoration.
    internal_mutant = copy.deepcopy(document)
    internal_candidate = next((index, path, node.text) for index, math in enumerate(original_maths)
                              for path, node in paths(math) if tag(node) == "mo" and node.text == ","
                              and path not in allowed_punctuation_edits(math))
    index, path, old = internal_candidate
    internal_math = list(internal_mutant.iter("{" + MATH + "}math"))[index]
    at_path(internal_math, path).text = ""
    ledger = json.loads(internal_math.get(LEDGER, "[]"))
    ledger.append({"path": list(path), "old": old, "new": ""})
    internal_math.set(LEDGER, json.dumps(ledger, ensure_ascii=False))
    reject("mutation_reversible_internal_comma_edit_rejected", lambda: validate_math(internal_mutant, source), "punctuation_edit_position_whitelisted:")

    parenthesis_mutant = copy.deepcopy(document)
    combined = next((index, path) for index, math in enumerate(original_maths)
                    for path, node in paths(math) if node.text == "),")
    index, path = combined
    combined_math = list(parenthesis_mutant.iter("{" + MATH + "}math"))[index]
    at_path(combined_math, path).text = ""
    ledger = json.loads(combined_math.get(LEDGER))
    next(entry for entry in ledger if tuple(entry["path"]) == path)["new"] = ""
    combined_math.set(LEDGER, json.dumps(ledger, ensure_ascii=False))
    reject("mutation_protected_closing_parenthesis_rejected", lambda: validate_math(parenthesis_mutant, source), "ledger_new_matches_policy:")
    changed_digest = ("0" if image_digest[0] != "0" else "1") + image_digest[1:]
    reject("mutation_image_digest_rejected_without_asset_write",
           lambda: validate_image_digest(changed_digest, sha256(original), spec, notice), "original_image_digest_agreement")
    check("mutations_leave_reader_and_source_unchanged", first == READER.read_bytes()
          and sha256(excerpt) == manifest["excerpt_sha256"])
    final_hashes = {path.relative_to(BASE).as_posix(): sha256(path) for path in input_paths}
    check("checked_input_hashes_stable_during_run", final_hashes == initial_hashes)
    final_hashes[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {
        "unit": "PNB-004", "status": "structural_pass_linguistic_and_visual_review_separate",
        "translated_blocks": len(translation["source_blocks"]), "source_ids_preserved": len(identifiers),
        "math": math_report, "source_prose_numerals": numerals, "bilingual_key_words": key_words,
        "image": {"source_id": figure.get("id"), "path": spec["path"], "sha256": image_digest,
                  "width": dimensions[0], "height": dimensions[1]},
        "local_reference_count": len(local), "checks": checks, "hashes": final_hashes,
        "limitations": [
            "Native-speaker and educator review is pending; structural equality does not certify idiomatic Punjabi.",
            "Only the declared function-notation section is checked, not the whole module or full language assignment.",
            "Source examples and disclosed qualifications are preserved, not certified as universal time/age-function claims or a universal leap-year/domain definition.",
            "Bilingual-key presence is checked; its Punjabi meaning requires linguistic review.",
            "Image hash/dimensions are checked; raster semantics, desktop/mobile layout, font shaping and screen-reader pronunciation need separate visual/accessibility review.",
            "External web-link availability is not network-tested by this local QA script.",
        ],
    }
    (BASE / "qa").mkdir(exist_ok=True)
    (BASE / "qa/structural-004.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {len(identifiers)} source IDs; {math_report['trees']} MathML trees; "
          f"{math_report['text_edits']} reversible punctuation edits")


if __name__ == "__main__":
    main()
