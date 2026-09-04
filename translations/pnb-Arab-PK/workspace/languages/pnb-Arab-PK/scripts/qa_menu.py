"""Source-bound PNB-002 structural checks; no mathematical-formula certification.

Builds the menu reader twice and writes only its generated structural receipt.
Regression mutations operate on detached DOMs, never on translation files.
"""
from pathlib import Path, PurePosixPath
from decimal import Decimal
from urllib.parse import unquote, urlsplit
import copy
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
READER = BASE / "reader/unit-002.html"
MANIFEST = BASE / "source-excerpts/manifest-002.json"
NOTICES = BASE / "provenance/menu-component-notices.json"
TRANSLATION = BASE / "translations/unit-002.json"
MATH = "http://www.w3.org/1998/Math/MathML"
FORBIDDEN = re.compile(r"[\u0a00-\u0a7f\ufffd\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]")
DOLLAR = re.compile(r"\$(\d+\.\d{2})(?!\d)")


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def text(node):
    return "".join(node.itertext()).strip()


def sha256(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def element(document, identifier):
    found = [node for node in document.iter() if node.get("id") == identifier]
    require(f"exactly_one_element:{identifier}", len(found) == 1)
    return found[0]


def parse_reader(data):
    return ET.fromstring(data[data.index("<html"):])


def source_pairs(source):
    """Expand the shared price in the actual English source alt, not a fixture."""
    pattern = re.compile(
        r"\bwhere a (?P<one>.+?) is \$(?P<price_one>\d+\.\d{2}) "
        r"and a (?P<two>.+?) and (?P<three>.+?) are "
        r"\$(?P<price_shared>\d+\.\d{2})\.", re.IGNORECASE,
    )
    witnesses = []
    for media in source.iter():
        if tag(media) != "media" or "$" not in media.get("alt", ""):
            continue
        match = pattern.search(media.get("alt", ""))
        require(f"recognized_source_price_alt:{media.get('id')}", match is not None)
        witnesses.append([
            (match["one"].title(), match["price_one"]),
            (match["two"].title(), match["price_shared"]),
            (match["three"].title(), match["price_shared"]),
        ])
    require("source_price_alt_witnesses_present", bool(witnesses))
    require("source_price_alt_witnesses_agree", all(pairs == witnesses[0] for pairs in witnesses))
    return witnesses[0]


def priced_legend_rows(document):
    legend = element(document, "menu-legend")
    rows = []
    for row in legend.findall("./ul/li"):
        amounts = [node for node in row.iter("bdi") if "$" in text(node)]
        if not amounts:
            continue
        labels = [node for node in row.iter("bdi") if node.get("lang") == "en"]
        require("one_label_and_price_per_menu_row", len(labels) == len(amounts) == 1)
        require("menu_row_price_is_decimal_dollars", DOLLAR.fullmatch(text(amounts[0])) is not None)
        rows.append((row, labels[0], amounts[0]))
    return rows


def validate_menu(document, expected_pairs):
    """The same source-bound semantic validator checks real and mutated DOMs."""
    legend = element(document, "menu-legend")
    require("legend_marked_original", legend.get("data-origin") == "original-bridge")
    rows = priced_legend_rows(document)
    displayed = [(text(label), text(amount)[1:]) for _, label, amount in rows]
    require("displayed_menu_matches_source_product_price_pairs", displayed == expected_pairs)
    require("displayed_menu_labels_and_prices_ltr", all(
        label.get("dir") == amount.get("dir") == "ltr" for _, label, amount in rows
    ))
    return displayed


def source_lists(source):
    return [node for node in source.iter() if tag(node) == "list"]


def validate_parts(document, source):
    """Anonymous source items are matched by their identified list and position."""
    checked = []
    source_ids = {node.get("id") for node in source.iter() if node.get("id")}
    for source_list in source_lists(source):
        identifier = source_list.get("id")
        target_list = element(document, identifier)
        source_items = [node for node in source_list if tag(node) == "item"]
        target_items = target_list.findall("li")
        require(f"source_list_item_count:{identifier}", len(source_items) == len(target_items))
        require(f"source_list_semantics:{identifier}", target_list.tag == "ol" and target_list.get("role") == "list")
        for index, (original, rendered) in enumerate(zip(source_items, target_items), 1):
            key = f"{identifier}/item/{index}"
            tokens = [node for node in original if tag(node) == "span" and node.get("class") == "token"]
            require(f"one_source_part_token:{key}", len(tokens) == 1)
            expected_label = "(" + unicodedata.normalize("NFKC", text(tokens[0])) + ")"
            require(f"part_label_first_and_ltr:{key}", len(rendered) > 0 and
                    rendered[0].tag == "bdi" and rendered[0].get("dir") == "ltr" and
                    text(rendered[0]) == expected_label and not (rendered.text or "").strip())
            expected_children = [node.get("id") for node in original
                                 if tag(node) in ("figure", "para")]
            actual_children = [node.get("id") for node in rendered if node.get("id") in source_ids]
            require(f"source_item_children_match:{key}", actual_children == expected_children)
            expected_descendants = [node.get("id") for node in original.iter() if node.get("id")]
            actual_descendants = [node.get("id") for node in rendered.iter() if node.get("id") in source_ids]
            require(f"source_item_descendants_match:{key}", actual_descendants == expected_descendants)
            checked.append({"source_key": key, "label": expected_label,
                            "immediate_source_children": expected_children})
    return checked


def validate_source_links(document, source, figure_specs):
    source_parents = {child: parent for parent in source.iter() for child in parent}
    checked = []
    for owner in source.iter():
        links = [node for node in owner if tag(node) == "link"]
        if not links:
            continue
        if owner.get("id"):
            rendered = element(document, owner.get("id"))
            key = owner.get("id")
        else:
            require("anonymous_link_owner_is_item", tag(owner) == "item")
            source_list = source_parents[owner]
            source_items = [node for node in source_list if tag(node) == "item"]
            position = source_items.index(owner)
            rendered = element(document, source_list.get("id")).findall("li")[position]
            key = f"{source_list.get('id')}/item/{position + 1}"
        expected = ["#" + node.get("target-id") for node in links]
        actual = [node for node in rendered if node.tag == "a"]
        require(f"direct_source_link_targets:{key}", [node.get("href") for node in actual] == expected)
        for link in actual:
            target = link.get("href")[1:]
            labels = link.findall("bdi")
            require(f"local_figure_link_label:{target}", len(labels) == 1 and
                    labels[0].get("dir") == "ltr" and text(labels[0]) == figure_specs[target]["local_label"])
        checked.extend(expected)
    example = next(node for node in source if tag(node) == "example")
    actual = [node.get("href") for node in element(document, example.get("id")).iter("a")
              if node.get("href", "").startswith("#")]
    require("all_source_link_targets_and_order_exact", actual == checked)
    return checked


def validate_directions(document):
    parents = {child: parent for parent in document.iter() for child in parent}

    def ancestors(node):
        while node is not None:
            yield node
            node = parents.get(node)

    def direction(node):
        return next((ancestor.get("dir") for ancestor in ancestors(node) if ancestor.get("dir")), None)

    require("all_bdi_explicit_ltr", all(node.get("dir") == "ltr" for node in document.iter("bdi")))
    require("english_lanes_ltr", all(direction(node) == "ltr" for node in document.iter()
                                    if node.get("lang") == "en"))
    for node in document.find("body").iter():
        fragments = [(node, node.text or "")] + [(node, child.tail or "") for child in node]
        for owner, fragment in fragments:
            if re.search(r"[A-Za-z]", fragment):
                require("visible_english_is_in_ltr_context", direction(owner) == "ltr")
            if "$" in fragment:
                require("visible_dollars_are_bdi_ltr", any(
                    ancestor.tag == "bdi" and ancestor.get("dir") == "ltr" for ancestor in ancestors(owner)
                ))


def validate_local_references(document):
    references = []
    for node in document.iter():
        for attribute in ("href", "src"):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
            parsed = urlsplit(value)
            if parsed.scheme in ("https", "http", "mailto"):
                continue
            require(f"supported_local_reference:{value}", not parsed.scheme and not parsed.netloc)
            target = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER
            require(f"local_reference_exists:{value}", target.is_file())
            if parsed.fragment:
                target_doc = document if target == READER.resolve() else parse_reader(target.read_text(encoding="utf-8"))
                require(f"local_fragment_exists:{value}", any(
                    candidate.get("id") == unquote(parsed.fragment) for candidate in target_doc.iter()
                ))
            references.append(value)
    return references


def jpeg_dimensions(data):
    """Read JPEG SOF dimensions without a rasterization dependency."""
    require("jpeg_start_marker", data[:2] == b"\xff\xd8")
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset < len(data):
        require("jpeg_marker_prefix", data[offset] == 0xFF)
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], "big")
        require("jpeg_segment_in_bounds", length >= 2 and offset + length <= len(data))
        if marker in sof:
            return (int.from_bytes(data[offset + 5:offset + 7], "big"),
                    int.from_bytes(data[offset + 3:offset + 5], "big"))
        require("jpeg_sof_before_scan", marker != 0xDA)
        offset += length
    raise AssertionError("jpeg_sof_dimensions_found")


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    notices = json.loads(NOTICES.read_text(encoding="utf-8"))
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    source = ET.parse(excerpt).getroot()
    specs = {entry["figure_id"]: entry for entry in manifest["images"]}
    notice_by_path = {entry["asset_path"]: entry for entry in notices}
    input_paths = [TRANSLATION, excerpt, MANIFEST, NOTICES,
                   BASE / "styles/reader.css", BASE / "terminology.tsv",
                   BASE / "scripts/build.py", Path(__file__).resolve(),
                   BASE / "provenance/ATTRIBUTION.md",
                   *[BASE / entry["path"] for entry in manifest["images"]]]
    start_hashes = {str(path.relative_to(BASE)): sha256(path) for path in input_paths}
    command = [sys.executable, str(BASE / "scripts/build.py"), "--unit", "002"]
    subprocess.run(command, check=True)
    first = READER.read_bytes()
    subprocess.run(command, check=True)
    require("deterministic_reader_build", first == READER.read_bytes())
    reader_text = first.decode("utf-8")
    document = parse_reader(reader_text)
    translation = json.loads(TRANSLATION.read_text(encoding="utf-8"))
    checks = ["deterministic_reader_build"]

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    check("frozen_excerpt_hash_matches_manifest", sha256(excerpt) == manifest["excerpt_sha256"])
    check("exact_locale_and_rtl", document.get("lang") == translation["locale"] == "pnb-Arab-PK"
          and document.get("dir") == "rtl")
    check("exact_unit_scope", translation["unit"] == manifest["unit"] == "PNB-002"
          and [node.get("id") for node in source if tag(node) == "example"] == ["Example_01_01_01"])
    for path in [*input_paths, READER]:
        if path.suffix.lower() not in (".jpg", ".jpeg"):
            check(f"unicode_clean:{path.relative_to(BASE).as_posix()}", not FORBIDDEN.search(path.read_text(encoding="utf-8")))
    check("no_unresolved_placeholders", not re.search(r"\{\{[^{}]*\}\}|\bTODO\b", reader_text))
    ids = [node.get("id") for node in document.iter() if node.get("id")]
    source_ids = [node.get("id") for node in source.iter() if node is not source and node.get("id")]
    check("unique_html_ids", len(ids) == len(set(ids)))
    check("all_source_ids_retained_in_document_order", [identifier for identifier in ids if identifier in set(source_ids)] == source_ids)
    check("excerpt_wrapper_not_rendered", source.get("id") not in ids)
    source_parents = {child: parent for parent in source.iter() for child in parent}
    target_parents = {child: parent for parent in document.iter() for child in parent}

    def identified_ancestors(node, parents):
        ancestors = []
        while node in parents:
            node = parents[node]
            if node.get("id") in source_ids:
                ancestors.append(node.get("id"))
        return ancestors

    check("source_id_ancestor_chains_preserved", all(
        identified_ancestors(node, source_parents)
        == identified_ancestors(element(document, node.get("id")), target_parents)
        for node in source.iter() if node is not source and node.get("id")
    ))
    parts = validate_parts(document, source)
    checks.extend(["question_and_solution_labels_follow_source_order", "nested_figures_and_paragraphs_stay_in_source_parts"])
    link_targets = validate_source_links(document, source, specs)
    checks.append("source_link_targets_owners_order_and_local_labels_exact")
    validate_directions(document)
    checks.extend(["all_bdi_explicit_ltr", "english_lanes_and_visible_english_ltr", "visible_dollars_bdi_ltr"])
    local_references = validate_local_references(document)
    checks.append("all_local_files_and_fragment_links_resolve")
    source_math = list(source.iter("{" + MATH + "}math"))
    target_math = [node for node in document.iter() if tag(node) == "math"]
    check("no_mathml_in_this_source_or_reader", not source_math and not target_math)
    check("partial_coverage_disclosed", "پورے حصے دا ترجمہ نہیں" in reader_text)

    expected_pairs = source_pairs(source)
    displayed_pairs = validate_menu(document, expected_pairs)
    checks.extend(["menu_product_price_pairs_match_actual_source_alt", "menu_legend_original_and_ltr"])
    item_outputs = {}
    price_outputs = {}
    for item, price in displayed_pairs:
        item_outputs.setdefault(item, set()).add(price)
        price_outputs.setdefault(price, set()).add(item)
    check("displayed_item_to_price_function_price_to_item_not_function",
          all(len(outputs) == 1 for outputs in item_outputs.values())
          and any(len(outputs) > 1 for outputs in price_outputs.values()))

    source_figures = [node for node in source.iter() if tag(node) == "figure"]
    check("all_three_original_figures_declared_once", len(source_figures) == len(specs) == len(manifest["images"]) == len(notices) == len(notice_by_path) == 3
          and [node.get("id") for node in source_figures] == list(specs))
    check("reader_image_count_matches_source", len(list(document.iter("img"))) == len(source_figures))
    image_checks = []
    repo_name = manifest["upstream_url"].rstrip("/").rsplit("/", 1)[-1]
    original_root = WORKSPACE / "downloads/complete-upstream" / repo_name
    for figure in source_figures:
        figure_id = figure.get("id")
        spec = specs[figure_id]
        media = next(node for node in figure if tag(node) == "media")
        source_image = next(node for node in media if tag(node) == "image")
        rendered_figure = element(document, figure_id)
        rendered_images = list(rendered_figure.iter("img"))
        check(f"figure_owns_original_media_id:{figure_id}", len(rendered_images) == 1 and rendered_images[0].get("id") == media.get("id"))
        rendered_image = rendered_images[0]
        local_image = BASE / spec["path"]
        original_image = original_root / spec["source_path"]
        notice = notice_by_path[spec["source_path"]]
        check(f"figure_source_image_path:{figure_id}", PurePosixPath(source_image.get("src")).name == PurePosixPath(spec["source_path"]).name
              and (READER.parent / rendered_image.get("src")).resolve() == local_image.resolve())
        image_hash = sha256(local_image)
        check(f"original_image_and_retained_notice_hashes:{figure_id}", image_hash == sha256(original_image) == spec["sha256"] == notice["sha256"]
              and local_image.stat().st_size == int(notice["bytes"]))
        dimensions = jpeg_dimensions(local_image.read_bytes())
        check(f"original_image_dimensions:{figure_id}", dimensions == (spec["width"], spec["height"])
              == (int(rendered_image.get("width")), int(rendered_image.get("height"))))
        actual_alt = rendered_image.get("alt", "")
        check(f"translated_alt_retained:{figure_id}", actual_alt == translation["source_blocks"][media.get("id") + "/alt"]
              and bool(re.search(r"[\u0600-\u06ff]", actual_alt)))
        check(f"source_alt_dollar_values_unchanged:{figure_id}", DOLLAR.findall(actual_alt) == DOLLAR.findall(media.get("alt", ""))
              and not re.search(r"\$\d+,\d{2}", actual_alt))
        image_checks.append({"figure_id": figure_id, "asset": spec["path"], "source_asset": spec["source_path"],
                             "sha256": image_hash, "width": dimensions[0], "height": dimensions[1]})

    # Reuse real validators on copied DOMs; never alter the real JSON or HTML.
    price_mutant = copy.deepcopy(document)
    amount = priced_legend_rows(price_mutant)[0][2]
    old_amount = text(amount)
    amount.text = f"${Decimal(old_amount[1:]) + Decimal('0.01'):.2f}"
    try:
        validate_menu(price_mutant, expected_pairs)
    except AssertionError as error:
        check("mutation_changed_displayed_price_rejected", str(error) == "displayed_menu_matches_source_product_price_pairs")
    else:
        raise AssertionError("mutation_changed_displayed_price_not_rejected")

    figure_mutant = copy.deepcopy(document)
    solution = next(node for node in source.iter() if tag(node) == "solution")
    solution_list = next(node for node in solution if tag(node) == "list")
    rendered_items = element(figure_mutant, solution_list.get("id")).findall("li")
    figures = [next(node for node in item if node.tag == "figure") for item in rendered_items]
    require("two_solution_figures_for_swap", len(figures) == 2)
    positions = [list(item).index(figure) for item, figure in zip(rendered_items, figures)]
    for item, figure in zip(rendered_items, figures):
        item.remove(figure)
    rendered_items[0].insert(positions[0], figures[1])
    rendered_items[1].insert(positions[1], figures[0])
    try:
        validate_parts(figure_mutant, source)
    except AssertionError as error:
        check("mutation_switched_solution_figures_rejected",
              str(error) == f"source_item_children_match:{solution_list.get('id')}/item/1")
    else:
        raise AssertionError("mutation_switched_solution_figures_not_rejected")
    check("mutation_tests_do_not_change_reader", READER.read_bytes() == first)
    final_hashes = {str(path.relative_to(BASE)): sha256(path) for path in input_paths}
    check("checked_inputs_unchanged_during_run", final_hashes == start_hashes)
    final_hashes[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {
        "unit": "PNB-002", "status": "structural_pass_linguistic_and_visual_review_separate",
        "translated_blocks": len(translation["source_blocks"]), "source_ids_preserved": len(source_ids),
        "source_math_count": len(source_math), "formula_validation": "not_applicable_no_source_mathml",
        "source_link_targets": link_targets, "source_parts": parts,
        "displayed_menu": [{"english_item": item, "usd": price} for item, price in displayed_pairs],
        "images": image_checks, "local_reference_count": len(local_references),
        "checks": checks, "hashes": {name.replace("\\", "/"): digest for name, digest in final_hashes.items()},
        "limitations": [
            "No native-speaker or educator approval claimed; structural checks cannot certify idiomatic Punjabi.",
            "Only Example_01_01_01 is covered, not the complete m49301 module or the language allocation.",
            "No source MathML occurs here; no formula or mathematical-tree validation is claimed.",
            "Menu products and prices are parsed from source alt prose and checked against the displayed legend; no automated raster OCR is claimed.",
            "Original image hashes and dimensions are checked; visual inspection of their English content and desktop/mobile rendering is separate.",
            "Alt attributes are plain text; screen-reader pronunciation and cross-machine font shaping need separate review.",
            "External web links are retained but not network-tested by this local structural check.",
        ],
    }
    (BASE / "qa").mkdir(exist_ok=True)
    (BASE / "qa/structural-002.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {len(source_ids)} retained IDs; {len(source_figures)} original figures; no source MathML")


if __name__ == "__main__":
    main()
