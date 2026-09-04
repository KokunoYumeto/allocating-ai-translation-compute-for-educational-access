"""Finite source, fixture, route, asset, and narration checks for A10 like terms.

The module deliberately has no algebra or MathML-to-speech parser.  Production
readout is dispatched only from the exact reviewed whole-node fixtures in
``a10-combine-like-terms.rules.json`` after current live source/target trees,
rules bytes, assets, and the real cross-unit destination have been validated.
"""
from __future__ import annotations

import copy
import base64
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

from PIL import Image

from build import CN, MATH, XML_LANG, local, translated
from config import LANG, ROOT, TRACKS


UNIT = "a10-combine-like-terms"
MODULE = "m82453"
SECTION = "fs-id1170655163482"
EVALUATION_SECTION = "fs-id1170654889475"
EVALUATION_TARGET = "fs-id1170655171250"
ROUTE = "a10-evaluate-expressions.html#fs-id1170655171250"
RULES_PATH = LANG / f"audio/{UNIT}.rules.json"
EDITS_PATH = LANG / f"translation/{UNIT}.edits.json"
ASSETS_PATH = LANG / f"translation/{UNIT}.assets.json"
ID_PATH = ROOT / "downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml"
EN_PATH = ROOT / "downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml"
LOCK_PATH = LANG / "sources.lock.json"
SHARED_EDITS_PATH = LANG / "translation/phrases.json"
EVALUATION_READER = LANG / "review/units/a10-evaluate-expressions.html"

EXPECTED = {
    "rules": "2f597622bb356a22904b73c5c44b85e870d685c1d2e36f1e1bc3d9ce030920f1",
    "edits": "6281cd18f6251b0b7315567138ff9da253ed04fc99f0be470ddef023239283cd",
    "shared_edits": "adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8",
    "source_lock": "27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb",
    "id_module": "2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635",
    "en_module": "a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed",
}

LINGUISTIC_ATTRIBUTES = ("alt", "aria-label", "summary", XML_LANG)
PRIMARY_GROUPS = (
    "prose_fixtures",
    "heading_fixtures",
    "chart_fixtures",
    "math_layout_fixtures",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def tree_key(element: ET.Element) -> str:
    element = copy.deepcopy(element)
    element.tail = None
    return ET.canonicalize(
        ET.tostring(element, encoding="unicode"),
        strip_text=True,
        rewrite_prefixes=True,
    )


def tree_sha(element: ET.Element) -> str:
    return sha(tree_key(element).encode("utf-8"))


def parse_fixture(fragment: str) -> ET.Element:
    return ET.fromstring(fragment)


def node_at(root: ET.Element, path: list[int] | tuple[int, ...]) -> ET.Element:
    node = root
    for index in path:
        node = node[index]
    return node


def walk_paths(root: ET.Element):
    def visit(node: ET.Element, path: tuple[int, ...]):
        yield path, node
        for index, child in enumerate(node):
            yield from visit(child, path + (index,))
    yield from visit(root, ())


def one_by_id(root: ET.Element, identity: str) -> ET.Element:
    matches = [node for node in root.iter() if node.get("id") == identity]
    if len(matches) != 1:
        raise ValueError(f"source_identity_cardinality:{identity}:{len(matches)}")
    return matches[0]


def select_section(module_root: ET.Element, section_id: str) -> ET.Element:
    selected = copy.deepcopy(one_by_id(module_root, section_id))
    selected.tail = None
    return selected


def linguistic_attributes(node: ET.Element) -> dict[str, str]:
    return {name: node.attrib[name] for name in LINGUISTIC_ATTRIBUTES if name in node.attrib}


def target_for(source: ET.Element, track: str, edits: dict) -> ET.Element:
    if track == "id-academic":
        return copy.deepcopy(source)
    return translated(source, track, edits)


def _parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}


def containing_section(root: ET.Element, node: ET.Element) -> ET.Element:
    parents = _parent_map(root)
    current = node
    while current is not root:
        if local(current) == "section":
            return current
        current = parents[current]
    if local(root) == "section":
        return root
    raise ValueError("destination_not_in_section")


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag == "a" and "href" in values:
            self.hrefs.append(values["href"])


def verify_external_destination(id_module: ET.Element, en_module: ET.Element, rules: dict) -> dict:
    fixture = rules["reference_fixtures"][0]
    assert fixture["target_id"] == EVALUATION_TARGET
    assert fixture["target_scope"] == "a10-evaluate-expressions"
    assert fixture["expected_route_proposal"] == ROUTE
    result = {}
    for language, module_root, full_sha in (
        ("id", id_module, EXPECTED["id_module"]),
        ("en", en_module, EXPECTED["en_module"]),
    ):
        witness = fixture["external_destination"][language]
        assert witness["full_module_sha256"] == full_sha
        target = one_by_id(module_root, EVALUATION_TARGET)
        assert target.tag == witness["tag"]
        assert tree_sha(target) == witness["target_tree_sha256"]
        section = containing_section(module_root, target)
        assert section.get("id") == witness["section"] == EVALUATION_SECTION
        result[language] = witness["target_tree_sha256"]
    return result


def verify_route_reader(*, required: bool) -> dict:
    if not EVALUATION_READER.is_file():
        if required:
            raise ValueError("missing_exact_cross_unit_destination_reader")
        return {"route": ROUTE, "status": "destination_reader_dependency_pending"}
    raw = EVALUATION_READER.read_bytes()
    parser = AnchorParser()
    parser.feed(raw.decode("utf-8"))
    if parser.ids.count(EVALUATION_TARGET) != 1:
        raise ValueError("cross_unit_destination_fragment_not_unique")
    return {
        "route": ROUTE,
        "status": "verified_existing_destination_reader",
        "destination_reader_sha256": sha(raw),
        "destination_fragment_count": 1,
    }


def verify_assets(rules: dict, rules_raw: bytes) -> dict:
    raw = ASSETS_PATH.read_bytes()
    manifest = json.loads(raw)
    assert manifest["schema"] == "jv-like-terms-assets-v1"
    assert manifest["unit"] == UNIT
    assert manifest["rules_sha256"] == sha(rules_raw)
    assert manifest["source_assets"] == 3
    assert manifest["javanese_derivatives"] == 6
    assert manifest["indonesian_derivatives"] == 0
    assert len(manifest["assets"]) == len(rules["chart_fixtures"]) == 3
    derivative_count = 0
    for chart, asset in zip(rules["chart_fixtures"], manifest["assets"]):
        source = chart["primary_asset"]
        binding = asset["source_binding"]
        assert asset["fixture"] == chart["id"]
        assert asset["source_src"] == chart["source_image"]
        assert binding == {
            "module": MODULE,
            "section": SECTION,
            "media_id": chart["media_id"],
            "source_path": chart["source_path"],
            "source_tree_sha256": chart["source_tree_sha256"],
            "archive": rules["asset_binding"]["canonical_archive"],
            "archive_member": source["archive_member"],
            "old_visible_label": chart["source_visible_label"],
            "source_image_sha256": source["sha256"],
            "source_bytes": source["bytes"],
            "source_dimensions": source["dimensions"],
        }
        assert asset["derivative_method"] == {
            "method": "embed_exact_source_JPEG_and_cover_only_left_instruction_panel",
            "instruction_cover": {"x": 2, "y": 2, "width": 354, "height": source["dimensions"][1] - 4, "fill": "#a0b3bd"},
            "preserved_source_divider_x": [356, 357],
            "preserved_formula_panel_starts_x": 358,
            "latent_english_pixels": "retained_in_embedded_JPEG_beneath_opaque_cover",
        }
        assert len(asset["corrections"]) == 2
        for track, output in asset["outputs"].items():
            output_raw = (LANG / output["path"]).read_bytes()
            assert sha(output_raw) == output["sha256"]
            assert len(output_raw) == output["bytes"]
            assert output["dimensions"] == source["dimensions"]
            if track == "id-academic":
                assert output["mime_type"] == "image/jpeg"
                assert output_raw.startswith(b"\xff\xd8\xff")
                assert sha(output_raw) == source["sha256"]
                with Image.open(BytesIO(output_raw)) as image:
                    assert image.format == "JPEG" and list(image.size) == source["dimensions"]
                continue
            derivative_count += 1
            assert track in ("jv-academic", "jv-conversation")
            assert output["mime_type"] == "image/svg+xml"
            svg = ET.fromstring(output_raw)
            width, height = source["dimensions"]
            assert svg.get("width") == str(width) and svg.get("height") == str(height)
            assert svg.get("viewBox") == f"0 0 {width} {height}"
            assert svg.get("data-fixture") == chart["id"]
            assert svg.get("data-media-id") == chart["media_id"]
            assert svg.get("data-source-sha256") == source["sha256"]
            assert svg.get("data-track") == track
            title = next(node for node in svg if local(node) == "title")
            assert "".join(title.itertext()) == chart["expected_jv_visible_labels"][track]
            description = next(node for node in svg if local(node) == "desc")
            assert "".join(description.itertext()) == chart["expected_target_alt"][track]
            children = list(svg)
            embedded = next(node for node in children if local(node) == "image" and node.get("class") == "exact-source")
            group = next(node for node in children if local(node) == "g" and node.get("class") == "instruction-replacement")
            assert children.index(embedded) < children.index(group)
            assert (embedded.get("x"), embedded.get("y"), embedded.get("width"), embedded.get("height")) == (
                "0", "0", str(width), str(height))
            scheme, encoded = embedded.get("href").split(",", 1)
            assert scheme == "data:image/jpeg;base64"
            assert base64.b64decode(encoded, validate=True) == (LANG / asset["outputs"]["id-academic"]["path"]).read_bytes()
            assert group.get("clip-path") == "url(#instruction-clip)"
            cover = next(node for node in group if local(node) == "rect")
            assert (cover.get("x"), cover.get("y"), cover.get("width"), cover.get("height"), cover.get("fill")) == (
                "2", "2", "354", str(height - 4), "#a0b3bd")
            instructions = [node for node in svg.iter() if local(node) == "text" and node.get("class") == "instruction"]
            assert len(instructions) == 1
            pieces = [text.strip() for text in instructions[0].itertext() if text.strip()]
            assert " ".join(pieces) == chart["expected_jv_visible_labels"][track]
            if chart["id"] == "A10-COMB-D01":
                assert instructions[0].get("x") == "12" and instructions[0].get("y") == "28"
            elif chart["id"] == "A10-COMB-D02":
                line_spans = [node for node in instructions[0] if local(node) == "tspan"]
                assert [(node.get("x"), node.get("y")) for node in line_spans] == [("12", "27"), ("12", "49")]
            else:
                assert instructions[0].get("x") == "12" and instructions[0].get("y") == "31"
            metadata_node = next(node for node in svg if local(node) == "metadata")
            metadata = json.loads("".join(metadata_node.itertext()))
            assert metadata["old_visible_label"] == chart["source_visible_label"]
            assert metadata["new_visible_label"] == chart["expected_jv_visible_labels"][track]
            assert metadata["source_sha256"] == source["sha256"]
            correction = next(row for row in asset["corrections"] if row["track"] == track)
            assert correction["module"] == MODULE and correction["section"] == SECTION
            assert correction["media_id"] == chart["media_id"]
            assert correction["source_path"] == chart["source_path"]
            assert correction["source_tree_sha256"] == chart["source_tree_sha256"]
            assert correction["source_image_sha256"] == source["sha256"]
            assert correction["old_value"] == chart["source_visible_label"]
            assert correction["new_value"] == chart["expected_jv_visible_labels"][track]
        if chart["id"] == "A10-COMB-D01":
            correction = asset["declared_alt_correction"]
            assert correction["old_value"] == chart["source_alt"]
            assert correction["new_values"] == chart["expected_target_alt"]
            assert correction["source_image_sha256"] == source["sha256"]
            assert correction["source_tree_sha256"] == chart["source_tree_sha256"]
        else:
            assert asset["declared_alt_correction"] is None
    assert derivative_count == 6
    return {"manifest_sha256": sha(raw), "source_assets": 3, "javanese_derivatives": derivative_count}


def verify_fixture(root: ET.Element, targets: dict[str, ET.Element], fixture: dict) -> None:
    source_node = node_at(root, fixture["source_path"])
    serialized = fixture.get("source_cnxml", fixture.get("source_mathml"))
    assert serialized is not None
    assert tree_key(source_node) == tree_key(parse_fixture(serialized))
    assert tree_sha(source_node) == fixture["source_tree_sha256"]
    for track, target in targets.items():
        target_node = node_at(target, fixture["source_path"])
        assert tree_sha(target_node) == fixture["expected_target_tree_sha256"][track]
        assert linguistic_attributes(target_node) == fixture["target_linguistic_attributes"][track]


def verify_primary_coverage(source: ET.Element, rules: dict) -> None:
    roots = [(group, row["id"], tuple(row["source_path"])) for group in PRIMARY_GROUPS for row in rules[group]]
    assert len(roots) == 45 + 10 + 3 + 2 == 60
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            if left[2][:len(right[2])] == right[2] or right[2][:len(left[2])] == left[2]:
                raise ValueError(f"overlapping_spoken_owner:{left[1]}:{right[1]}")
    nonspoken_paths = []
    for identity in rules["nonspoken_source_blocks"]:
        for path, node in walk_paths(source):
            if node.get("id") == identity:
                nonspoken_paths.append(path)
    assert rules["nonspoken_source_blocks"] == ["fs-id1171789962795"]
    assert len(nonspoken_paths) == 1
    unowned_structural = []
    for path, node in walk_paths(source):
        within = [row for row in roots if path[:len(row[2])] == row[2]]
        if len(within) > 1:
            raise ValueError("node_has_repeated_spoken_owner")
        if within:
            continue
        if any(path[:len(block)] == block for block in nonspoken_paths):
            continue
        if any(owner_path[:len(path)] == path for _, _, owner_path in roots):
            continue
        unowned_structural.append((path, local(node), node.text, node.tail, dict(node.attrib), len(node)))
    assert unowned_structural == [
        ((12, 0), "label", None, None, {}, 0),
        ((27, 0), "label", None, None, {}, 0),
    ]
    assert len(list(walk_paths(source))) == 744


def verify_finite_answers(rules: dict) -> None:
    """Recompute only the twelve declared exercises and two informal sums."""
    checks = rules["answer_policy"]["independent_checks"]
    rows = checks["exercise_checks"]
    assert len(rows) == 12 and sum(row["part_count"] for row in rows) == 19
    for row in rows:
        task = row["task"]
        if task == "identify_coefficient":
            computed = [term[0] for term in row["question_terms"]]
            assert computed == row["independently_computed"] == row["provided_answers"]
        elif task == "identify_like_terms":
            grouped = {}
            for coefficient, variable, power in row["question_terms"]:
                grouped.setdefault((variable, power), []).append([coefficient, variable, power])
            computed = [group for group in grouped.values() if len(group) > 1]
            normalize = lambda groups: sorted(sorted(tuple(term) for term in group) for group in groups)
            assert normalize(computed) == normalize(row["computed_groups"]) == normalize(row["provided_pair_order"])
            unmatched = [group[0] for group in grouped.values() if len(group) == 1]
            assert sorted(map(tuple, unmatched)) == sorted(map(tuple, row["diagnostic_unmatched_not_new_answer"]))
            if row["exercise_id"] == "fs-id1170655163424":
                assert row["source_explicit_unmatched_statement"] is None
                assert row["diagnostic_unmatched_not_new_answer"] == [[9, "y", 1]]
        elif task == "identify_terms":
            assert row["provided_answers"] == row["independently_computed"]
        elif task == "combine_like_terms":
            finite_terms = {
                "fs-id1170654940590": [[2, "x", 2], [3, "x", 1], [7, "", 0], [1, "x", 2], [4, "x", 1], [5, "", 0]],
                "fs-id1170655165458": [[3, "x", 2], [7, "x", 1], [9, "", 0], [7, "x", 2], [9, "x", 1], [8, "", 0]],
                "fs-id1170655106283": [[4, "y", 2], [5, "y", 1], [2, "", 0], [8, "y", 2], [4, "y", 1], [5, "", 0]],
            }[row["exercise_id"]]
            totals = {}
            order = []
            for coefficient, variable, power in finite_terms:
                key = (variable, power)
                if key not in totals:
                    totals[key] = 0
                    order.append(key)
                totals[key] += coefficient
            computed = [[totals[key], key[0], key[1]] for key in order]
            assert computed == row["independently_computed"] == row["provided_answer_coefficients"]
        else:
            raise ValueError("unsupported_finite_answer_task")
    assert checks["source_part_count"] == 19 and checks["exercise_count"] == 12
    assert checks["expanded_layout_middle_terms"] == 12
    assert checks["expanded_layout_middle_plus_signs"] == 11
    assert checks["expanded_layout_spacing_after_term"] == [[4, "1em"], [11, "1em"]]
    orange = list(map(int, checks["orange_digit_occurrences"][:4]))
    assert orange == [4, 7, 1, 12] and orange[0] + orange[1] + orange[2] == orange[3]
    assert checks["orange_digit_occurrences"][:4] == checks["orange_digit_occurrences"][4:]
    assert checks["worked_image_reordered_expression"] == "2x^2+x^2+3x+4x+7+5"
    assert checks["worked_image_final_expression"] == "3x^2+7x+12"
    assert all(row["computed"] == [[12, "x", 1]] for row in checks["informal_checks"])


def load_verified(*, require_route_reader: bool = True):
    rules_raw = RULES_PATH.read_bytes()
    edits_raw = EDITS_PATH.read_bytes()
    assert sha(rules_raw) == EXPECTED["rules"]
    assert sha(edits_raw) == EXPECTED["edits"]
    assert sha(SHARED_EDITS_PATH.read_bytes()) == EXPECTED["shared_edits"]
    assert sha(LOCK_PATH.read_bytes()) == EXPECTED["source_lock"]
    assert sha(ID_PATH.read_bytes()) == EXPECTED["id_module"]
    assert sha(EN_PATH.read_bytes()) == EXPECTED["en_module"]
    rules, edits = json.loads(rules_raw), json.loads(edits_raw)
    scope = rules["scope"]
    assert (scope["unit"], scope["module"], scope["section"], scope["complete_section"]) == (UNIT, MODULE, SECTION, True)
    assert scope["direct_child_slice_zero_based"] is None
    assert scope["edits_sha256"] == EXPECTED["edits"]
    assert scope["shared_edits_sha256"] == EXPECTED["shared_edits"]
    assert scope["source_lock_sha256"] == EXPECTED["source_lock"]
    assert scope["indonesian_sha256"] == EXPECTED["id_module"]
    assert scope["english_sha256"] == EXPECTED["en_module"]
    assert rules["matching_contract"]["broad_parser_authorized"] is False
    assert rules["matching_contract"]["generic_mathml_layout_parser_authorized"] is False
    assert rules["matching_contract"]["generic_cross_unit_reference_bypass_authorized"] is False
    id_module, en_module = ET.parse(ID_PATH).getroot(), ET.parse(EN_PATH).getroot()
    source, english = select_section(id_module, SECTION), select_section(en_module, SECTION)
    assert tree_sha(source) == scope["indonesian_section_canonical_sha256"]
    assert tree_sha(english) == scope["english_section_canonical_sha256"]
    assert len(source) == scope["source_direct_children"] == 35
    assert len(list(source.iter())) == scope["source_node_count"] == 744
    identities = [
        {"path": list(path), "qname": node.tag,
         "attributes": {name: value for name, value in node.attrib.items() if name not in LINGUISTIC_ATTRIBUTES}}
        for path, node in walk_paths(source)
    ]
    assert identities == rules["source_node_identity"]
    ids = [node.get("id") for node in source.iter() if node.get("id")]
    assert ids == scope["source_section_ids"] and len(ids) == len(set(ids)) == 108
    counts = Counter(local(node) for node in source.iter())
    assert dict(counts) == scope["source_counts"]
    assert [(index, local(node), node.get("id"), node.tag) for index, node in enumerate(source)] == [
        (row["index_zero_based"], row["tag"], row["id"], row["qname"])
        for row in scope["direct_children"]
    ]
    assert len(list(source.iter("{" + MATH + "}math"))) == 62
    assert len(list(source.iter("{" + MATH + "}msup"))) == 55
    targets = {track: target_for(source, track, edits) for track in TRACKS}
    for track, target in targets.items():
        assert tree_sha(target) == scope["target_section_canonical_sha256"][track]
    expected_fixture_counts = {
        "math_fixtures": 62,
        "prose_fixtures": 45,
        "heading_fixtures": 10,
        "chart_fixtures": 3,
        "math_layout_fixtures": 2,
        "reference_fixtures": 1,
    }
    for group, count in expected_fixture_counts.items():
        assert len(rules[group]) == count
        for fixture in rules[group]:
            assert fixture["module"] == MODULE and fixture["section"] == SECTION
            verify_fixture(source, targets, fixture)
    assert [row["id"] for row in rules["math_fixtures"]] == [f"A10-COMB-M{i:02}" for i in range(1, 63)]
    prose = {row["id"]: row for row in rules["prose_fixtures"]}
    for fixture in rules["math_fixtures"]:
        path_node = node_at(source, fixture["source_path"])
        assert path_node.tag == "{" + MATH + "}math"
        anchor = one_by_id(source, fixture["anchor"])
        maths = list(anchor.iter("{" + MATH + "}math"))
        assert maths[fixture["math_ordinal"] - 1] is path_node
        english_node = node_at(english, fixture["source_path"])
        assert tree_key(english_node) == tree_key(parse_fixture(fixture["source_english_mathml"]))
        if fixture["standalone_readout_authorized"]:
            assert fixture["id"] in ("A10-COMB-M10", "A10-COMB-M56")
        else:
            owner = prose[fixture["requires_prose_fixture"]]
            assert owner["element_id"] == fixture["requires_prose_element"]
            owner_path = tuple(owner["source_path"])
            assert tuple(fixture["source_path"])[:len(owner_path)] == owner_path
            assert fixture["id"] in owner["contained_math_fixture_ids"]
    assert sum(row["standalone_readout_authorized"] for row in rules["math_fixtures"]) == 2
    assert sum(not row["standalone_readout_authorized"] for row in rules["math_fixtures"]) == 60
    for layout in rules["math_layout_fixtures"]:
        math = next(row for row in rules["math_fixtures"] if row["id"] == layout["math_fixture_id"])
        layout_path = tuple(layout["source_path"])
        math_path = tuple(math["source_path"])
        assert layout_path[:len(math_path)] == math_path
        assert layout["expected"] == math["expected"]
    reference = rules["reference_fixtures"][0]
    owner = prose[reference["readout_owned_by_prose_fixture"]]
    assert tuple(reference["source_path"])[:len(owner["source_path"])] == tuple(owner["source_path"])
    assert reference["visible_text_mutation_authorized"] is False
    verify_external_destination(id_module, en_module, rules)
    route = verify_route_reader(required=require_route_reader)
    assets = verify_assets(rules, rules_raw)
    verify_primary_coverage(source, rules)
    verify_finite_answers(rules)
    policy = rules["answer_policy"]
    boundaries = policy["exercise_boundaries"]
    assert len(boundaries) == policy["exercise_count"] == 12
    assert sum(row["question_parts"] for row in boundaries) == policy["question_parts"] == 19
    assert len(list(source.iter("{" + CN + "}exercise"))) == 12
    assert len(list(source.iter("{" + CN + "}solution"))) == 12
    titled = untitled = 0
    for boundary in boundaries:
        exercise = node_at(source, boundary["source_path"])
        assert exercise.get("id") == boundary["exercise_id"]
        assert tree_sha(exercise) == boundary["source_tree_sha256"]
        problem = one_by_id(exercise, boundary["problem_id"])
        solution = one_by_id(exercise, boundary["solution_id"])
        assert tree_sha(problem) == boundary["problem_source_tree_sha256"]
        assert tree_sha(solution) == boundary["solution_source_tree_sha256"]
        assert tree_key(problem) == tree_key(parse_fixture(boundary["problem_source_cnxml"]))
        assert tree_key(solution) == tree_key(parse_fixture(boundary["solution_source_cnxml"]))
        for track, target in targets.items():
            assert tree_sha(node_at(target, boundary["source_path"])) == boundary["expected_target_tree_sha256"][track]
        title = solution.find("{*}title")
        if boundary["answer_cue_mode"] == "exact_source_solution_title":
            titled += 1
            assert title is not None and boundary["solution_title_path"] is not None
            assert {track: node_at(targets[track], boundary["solution_title_path"]).text for track in TRACKS} == boundary["expected_cue"]
        else:
            untitled += 1
            assert title is None and boundary["solution_title_path"] is None
            assert boundary["expected_cue"] == policy["default_untitled_solution_cue"]
    assert (titled, untitled) == (4, 8)
    return {
        "rules": rules,
        "rules_raw": rules_raw,
        "edits": edits,
        "source": source,
        "english": english,
        "targets": targets,
        "assets": assets,
        "route": route,
    }


class NarrationBinding:
    """Authority for current, exact live nodes only; copies are unsupported."""

    def __init__(self, verified: dict, track: str) -> None:
        if track not in TRACKS:
            raise ValueError("unsupported_like_terms_track")
        self.track = track
        self.bound_track = track
        self.rules = verified["rules"]
        self.rules_sha256 = sha(verified["rules_raw"])
        self.rules_snapshot = sha(json.dumps(self.rules, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        self.source = verified["source"]
        self.target = verified["targets"][track]
        self.source_object = self.source
        self.target_object = self.target
        self.source_snapshot = tree_key(self.source)
        self.target_snapshot = tree_key(self.target)
        self.nodes = {}
        for group in PRIMARY_GROUPS:
            for fixture in self.rules[group]:
                node = node_at(self.target, fixture["source_path"])
                self.nodes[fixture["id"]] = (node, tree_key(node), fixture)

    def read(self, fixture_id: str, node: ET.Element) -> str:
        if sha(RULES_PATH.read_bytes()) != self.rules_sha256:
            raise ValueError("changed_like_terms_rules_after_binding")
        if self.track != self.bound_track or self.source is not self.source_object or self.target is not self.target_object:
            raise ValueError("changed_like_terms_binding_context")
        if sha(json.dumps(self.rules, ensure_ascii=False, sort_keys=True).encode("utf-8")) != self.rules_snapshot:
            raise ValueError("changed_like_terms_rules_after_binding")
        if tree_key(self.source) != self.source_snapshot or tree_key(self.target) != self.target_snapshot:
            raise ValueError("changed_live_like_terms_context")
        registered = self.nodes.get(fixture_id)
        if registered is None or registered[0] is not node or registered[1] != tree_key(node):
            raise ValueError("unsupported_source_bound_narration")
        return registered[2]["expected"][self.track]


def narration_blocks(verified: dict, track: str) -> list[tuple[str, str]]:
    binding = NarrationBinding(verified, track)
    entries = []
    for group in PRIMARY_GROUPS:
        for fixture in binding.rules[group]:
            node = node_at(binding.target, fixture["source_path"])
            mark = f'{MODULE}--{fixture["nearest_source_id"]}--{fixture["id"]}'
            entries.append((tuple(fixture["source_path"]), 1, mark, binding.read(fixture["id"], node), fixture["id"]))
    cue_count = 0
    for boundary in binding.rules["answer_policy"]["exercise_boundaries"]:
        if boundary["answer_cue_mode"] != "bound_untitled_solution_prefix":
            continue
        cue_count += 1
        cue_path = tuple(boundary["source_path"]) + (1, -1)
        mark = f'{MODULE}--{boundary["solution_id"]}--answer-cue'
        body = boundary["expected_cue"][track]
        entries.append((cue_path, 0, mark, body, "answer-cue"))
    assert cue_count == 8
    entries.sort(key=lambda row: (row[0], row[1]))
    for group in PRIMARY_GROUPS:
        for fixture in binding.rules[group]:
            owned = [body for _, _, _, body, fixture_id in entries if fixture_id == fixture["id"]]
            assert owned == [fixture["expected"][track]]
    blocks = [(mark, body) for _, _, mark, body, _ in entries]
    assert len(blocks) == len(dict(blocks)) == 68
    combined = "\n".join(body for _, body in blocks)
    assert all(body.strip() for _, body in blocks)
    assert not re.search(r"[0-9^=·$ⓐ-ⓩ]", combined)
    default_cue = binding.rules["answer_policy"]["default_untitled_solution_cue"][track]
    assert sum(body == default_cue for _, body in blocks) == 8
    p26 = next(row for row in binding.rules["prose_fixtures"] if row["id"] == "A10-COMB-P26")["expected"][track]
    unmatched = "sanga ping aksara ye" if track.startswith("jv") else "sembilan kali huruf ye"
    assert unmatched not in p26
    p36 = next(row for row in binding.rules["prose_fixtures"] if row["id"] == "A10-COMB-P36")["expected"][track]
    assert "?\n" in p36 and ("Wangsulan" if track.startswith("jv") else "Jawaban") in p36.split("?\n", 1)[1]
    assert binding.rules["nonspoken_source_blocks"] == ["fs-id1171789962795"]
    assert all("fs-id1171789962795" not in mark for mark, _ in blocks)
    return blocks


def validate_reader_route(page: str) -> None:
    parser = AnchorParser()
    parser.feed(page)
    assert parser.hrefs.count(ROUTE) == 3
    assert not any(href.endswith("#") or href == f"#{EVALUATION_TARGET}" for href in parser.hrefs)
    assert EVALUATION_TARGET not in parser.ids
