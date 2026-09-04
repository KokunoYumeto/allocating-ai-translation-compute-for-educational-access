"""TE-B020 pinned remainder, localization and narrow-bridge regressions."""
import copy
import unittest
import xml.etree.ElementTree as ET

from module_remainder_checks import (
    BASE,
    CN,
    CONTENT_UNITS,
    LINKS,
    MATH,
    MD,
    OBJECTIVES,
    PROTECTED,
    XH,
    bridge_baseline,
    catalog_baseline,
    ids_of,
    localize_catalog,
    module_baseline,
    source_baseline,
    validate_b020,
    validate_bridge,
    validate_catalog,
    validate_coverage,
    validate_module_graph,
    validate_remainder_source,
    validate_target,
)
from inspect_source import slots


def replace_text(root, before, after):
    for node in root.iter():
        for field in ("text", "tail"):
            value = getattr(node, field)
            if value and before in value:
                setattr(node, field, value.replace(before, after, 1))
                return
    raise AssertionError("Mutation text not found: " + before)


class ActualB020Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.metadata, cls.module = source_baseline()
        cls.catalog = catalog_baseline()
        cls.target = localize_catalog(cls.source, cls.catalog)
        cls.bridge = bridge_baseline()

    def test_complete_actual_report(self):
        result = validate_b020()
        self.assertEqual(
            {key: result[key] for key in (
                "module_elements", "module_slots", "module_ids",
                "content_elements", "content_slots", "remainder_elements", "remainder_slots",
                "target_elements", "target_slots", "target_ids", "localized_slots", "protected_slots",
                "objectives", "glossary_definitions", "bridge_ids", "support_links",
                "objective_links", "bridge_exercises", "bridge_equations",
            )},
            {
                "module_elements": 3576, "module_slots": 1958, "module_ids": 756,
                "content_elements": 3557, "content_slots": 1946,
                "remainder_elements": 19, "remainder_slots": 12,
                "target_elements": 19, "target_slots": 12, "target_ids": 4,
                "localized_slots": 10, "protected_slots": 2, "objectives": 5,
                "glossary_definitions": 1, "bridge_ids": 6, "support_links": 7,
                "objective_links": 5, "bridge_exercises": 0, "bridge_equations": 0,
            },
        )

    def test_exact_source_inventory_and_empty_content(self):
        self.assertEqual((len(list(self.source.iter())), len(list(slots(self.source))), len(ids_of(self.source))), (19, 12, 4))
        self.assertEqual(list(ids_of(self.source)), ["para-00001", "list-00001", "fs-id1226736", "fs-id1245763"])
        self.assertEqual(len(self.source.find(CN + "content")), 0)
        for name in ("exercise", "problem", "solution", "media", "image"):
            with self.subTest(name=name):
                self.assertEqual(list(self.source.iter(CN + name)), [])
        self.assertEqual(list(self.source.iter(MATH + "math")), [])

    def test_exact_protected_slots_and_titles(self):
        items = list(slots(self.target))
        self.assertEqual(items[1][0].tag, PROTECTED["s002"]["tag"])
        self.assertEqual(items[1][2], "m81244")
        self.assertEqual(items[9][0].tag, PROTECTED["s010"]["tag"])
        self.assertEqual(items[9][2], "8069044b-6fb1-49bf-b03a-64988f9b1ddd")
        self.assertEqual(self.target.findtext(CN + "title"), "పూర్ణాంకాలను కలపడం")
        self.assertEqual(self.target.findtext(CN + "metadata/" + MD + "title"), "పూర్ణాంకాలను కలపడం")

    def test_five_objectives_are_ordered_and_distinct(self):
        actual = tuple(node.text for node in self.target.findall(CN + "metadata/" + MD + "abstract/" + CN + "list/" + CN + "item"))
        self.assertEqual(actual, OBJECTIVES)
        self.assertEqual(len(set(actual)), 5)

    def test_one_complete_glossary_definition(self):
        definitions = self.target.findall(CN + "glossary/" + CN + "definition")
        self.assertEqual(len(definitions), 1)
        self.assertEqual(definitions[0].get("id"), "fs-id1226736")
        self.assertEqual(definitions[0].findtext(CN + "term"), "మొత్తం (sum)")
        meaning = definitions[0].find(CN + "meaning")
        self.assertEqual((meaning.get("id"), meaning.text), ("fs-id1245763", "రెండు లేదా అంతకంటే ఎక్కువ సంఖ్యలను కలిపితే వచ్చే ఫలితమే మొత్తం."))

    def test_exact_coverage_arithmetic_and_frozen_roots(self):
        result = validate_coverage(self.module, self.source, self.metadata)
        self.assertEqual(result, {
            "content_elements": 3557, "content_slots": 1946,
            "remainder_elements": 19, "remainder_slots": 12,
            "module_elements": 3576, "module_slots": 1958,
        })
        self.assertEqual(sum(row[2] for row in CONTENT_UNITS) + 19, 3576)
        self.assertEqual(sum(row[3] for row in CONTENT_UNITS) + 12, 1958)

    def test_objective_links_route_to_actual_frozen_sections(self):
        anchors = list(self.bridge.iter(XH + "a"))
        self.assertEqual(tuple(node.get("href") for node in anchors), tuple(row[0] for row in LINKS))
        for href, _ in LINKS:
            filename, fragment = href.split("#", 1)
            source = ET.parse(BASE / "sources" / (filename.removesuffix(".html") + ".en.cnxml")).getroot()
            self.assertIn(fragment, ids_of(source))

    def test_narrow_bridge_has_no_lesson_or_scoring_structures(self):
        forbidden = {"script", "form", "iframe", "img", "svg", "table", "details", "input", "button"}
        self.assertFalse(any(node.tag.rsplit("}", 1)[-1] in forbidden for node in self.bridge.iter()))
        self.assertEqual(len(self.bridge.findall(".//" + XH + "ul/" + XH + "li")), 5)
        self.assertIn("adds no source exercise, score or module-completion claim", " ".join("".join(self.bridge.itertext()).split()))

    def test_validator_is_read_only(self):
        paths = [
            BASE / "sources/TE-B020.en.cnxml",
            BASE / "sources/TE-B020.source.json",
            BASE / "translations/TE-B020.te.json",
            BASE / "translations/TE-B020.bridge.xhtml",
        ]
        before = {path: path.read_bytes() for path in paths}
        validate_b020()
        self.assertEqual(before, {path: path.read_bytes() for path in paths})


class CorruptionRejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.metadata, cls.module = source_baseline()
        cls.catalog = catalog_baseline()
        cls.target = localize_catalog(cls.source, cls.catalog)
        cls.bridge = bridge_baseline()

    def test_module_child_removal_and_reordering_rejected(self):
        changed = copy.deepcopy(self.module)
        changed.find(CN + "content").remove(changed.find(CN + "content")[-1])
        with self.assertRaisesRegex(AssertionError, "content-root order"):
            validate_module_graph(changed)
        changed = copy.deepcopy(self.module)
        changed[0], changed[1] = changed[1], changed[0]
        with self.assertRaisesRegex(AssertionError, "direct-child order"):
            validate_module_graph(changed)

    def test_source_content_duplication_rejected(self):
        changed = copy.deepcopy(self.source)
        changed.find(CN + "content").append(copy.deepcopy(self.module.find(CN + "content")[0]))
        with self.assertRaisesRegex(AssertionError, "duplicates lesson content"):
            validate_remainder_source(changed, self.metadata, self.module)

    def test_source_wrapper_text_or_id_corruption_rejected(self):
        changed = copy.deepcopy(self.source)
        changed.find(CN + "content").text = "changed"
        with self.assertRaisesRegex(AssertionError, "Content wrapper"):
            validate_remainder_source(changed, self.metadata, self.module)
        changed = copy.deepcopy(self.source)
        changed.find(CN + "glossary/" + CN + "definition").set("id", "changed")
        with self.assertRaisesRegex(AssertionError, "glossary differs"):
            validate_remainder_source(changed, self.metadata, self.module)

    def test_coverage_metadata_and_frozen_count_corruption_rejected(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["coverage"]["content_units"][0]["elements"] = 19
        with self.assertRaisesRegex(AssertionError, "coverage metadata"):
            validate_coverage(self.module, self.source, metadata)

    def test_catalog_protected_overlap_and_wrong_uuid_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["translations"]["s002"] = "మూల గుర్తింపు"
        with self.assertRaises(AssertionError):
            validate_catalog(catalog)
        catalog = copy.deepcopy(self.catalog)
        catalog["protected_slots"]["s010"]["value"] = "changed"
        with self.assertRaisesRegex(AssertionError, "protected slots"):
            validate_catalog(catalog)

    def test_catalog_missing_or_reordered_objective_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["translations"].pop("s007")
        with self.assertRaisesRegex(AssertionError, "translations changed"):
            validate_catalog(catalog)
        catalog = copy.deepcopy(self.catalog)
        catalog["translations"]["s005"], catalog["translations"]["s006"] = catalog["translations"]["s006"], catalog["translations"]["s005"]
        with self.assertRaisesRegex(AssertionError, "translations changed"):
            validate_catalog(catalog)

    def test_target_title_pair_corruption_rejected(self):
        changed = copy.deepcopy(self.target)
        changed.find(CN + "title").text = "మారిన శీర్షిక"
        with self.assertRaisesRegex(AssertionError, "target slot s001"):
            validate_target(self.source, changed, self.catalog)
        changed = copy.deepcopy(self.target)
        changed.find(CN + "metadata/" + MD + "title").text = "మారిన శీర్షిక"
        with self.assertRaisesRegex(AssertionError, "target slot s003"):
            validate_target(self.source, changed, self.catalog)

    def test_target_protected_values_rejected(self):
        for field, message in (("content-id", "s002"), ("uuid", "s010")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.target)
                changed.find(CN + "metadata/" + MD + field).text = "changed"
                with self.assertRaisesRegex(AssertionError, message):
                    validate_target(self.source, changed, self.catalog)

    def test_target_objective_reordering_rejected(self):
        changed = copy.deepcopy(self.target)
        items = changed.findall(CN + "metadata/" + MD + "abstract/" + CN + "list/" + CN + "item")
        items[0].text, items[1].text = items[1].text, items[0].text
        with self.assertRaisesRegex(AssertionError, "target slot s005"):
            validate_target(self.source, changed, self.catalog)

    def test_target_lesson_exercise_and_math_insertion_rejected(self):
        changed = copy.deepcopy(self.target)
        changed.find(CN + "content").append(ET.Element(CN + "exercise", {"id": "invented"}))
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_target(self.source, changed, self.catalog)
        changed = copy.deepcopy(self.target)
        changed.find(CN + "content").append(ET.Element(MATH + "math"))
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_target(self.source, changed, self.catalog)

    def test_target_glossary_corruption_and_duplication_rejected(self):
        changed = copy.deepcopy(self.target)
        changed.find(CN + "glossary/" + CN + "definition/" + CN + "meaning").text = "మారిన నిర్వచనం"
        with self.assertRaisesRegex(AssertionError, "target slot s012"):
            validate_target(self.source, changed, self.catalog)
        changed = copy.deepcopy(self.target)
        definition = changed.find(CN + "glossary/" + CN + "definition")
        changed.find(CN + "glossary").append(copy.deepcopy(definition))
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_target(self.source, changed, self.catalog)

    def test_bridge_link_missing_or_reordered_rejected(self):
        changed = copy.deepcopy(self.bridge)
        next(changed.iter(XH + "a")).set("href", "TE-B013.html#missing")
        with self.assertRaisesRegex(AssertionError, "links/order"):
            validate_bridge(changed)
        changed = copy.deepcopy(self.bridge)
        anchors = list(changed.iter(XH + "a"))
        anchors[0].set("href", LINKS[1][0])
        anchors[1].set("href", LINKS[0][0])
        with self.assertRaisesRegex(AssertionError, "links/order"):
            validate_bridge(changed)

    def test_bridge_objective_link_label_mismatch_rejected(self):
        changed = copy.deepcopy(self.bridge)
        replace_text(changed, OBJECTIVES[0], "వేరే లక్ష్యం")
        with self.assertRaisesRegex(AssertionError, "Objective/link mapping"):
            validate_bridge(changed)

    def test_bridge_lesson_structure_or_numeric_worked_example_rejected(self):
        changed = copy.deepcopy(self.bridge)
        changed.append(ET.Element(XH + "details"))
        with self.assertRaisesRegex(AssertionError, "lesson/assessment"):
            validate_bridge(changed)
        changed = copy.deepcopy(self.bridge)
        paragraph = ET.SubElement(changed, XH + "p")
        paragraph.text = "3+4=7"
        with self.assertRaisesRegex(AssertionError, "worked numeric lesson"):
            validate_bridge(changed)

    def test_bridge_disclosure_and_completion_boundary_rejected(self):
        changed = copy.deepcopy(self.bridge)
        replace_text(changed, "కొత్త పాఠం, ప్రశ్నల సమితి, మార్కుల ప్రమాణం", "కొత్త పాఠం")
        with self.assertRaisesRegex(AssertionError, "no-score disclosure"):
            validate_bridge(changed)
        changed = copy.deepcopy(self.bridge)
        replace_text(changed, "పూర్తయ్యాయని అనుకోకండి", "పూర్తయ్యాయి")
        with self.assertRaisesRegex(AssertionError, "Completion boundary"):
            validate_bridge(changed)


if __name__ == "__main__":
    unittest.main()
