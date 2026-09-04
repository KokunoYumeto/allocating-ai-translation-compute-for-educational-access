"""Read-only m81373 coverage reconciliation for MR-BRIDGE-001 through 010.

Run python -B tools/test_m81373_coverage.py (from the language directory), or
add --report for a JSON snapshot. PASS means the bounded inventory and recorded
gaps match; it does NOT mean complete translation, reader QA, or native review.
No downloads, archive extraction, builds, or file writes occur.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
ARCHIVE = BASE.parent / "downloads/mr-Deva-IN/releases/A20-canonical.zip"
PREFIX = "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/"
MEMBER = PREFIX + "modules/m81373/index.cnxml"
MODULE_SHA = "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
UNITS = tuple(f"MR-BRIDGE-{n:03d}" for n in range(1, 11))
READY = UNITS[:5]  # Parent's explicit 2026-08-31 status, not inferred from files.
LEGACY_SELECTORS = ("fs-id1167833175472", "fs-id1167836692527", "fs-id1167836521479", "fs-id1167829859398")
MISSING_WRAPPERS = {"fs-id1167826170977", "fs-id1167826189010"}
CONTEXTS = {
    "fs-id1167829789538": ("MR-BRIDGE-008", "संबंधाचा प्रांत आणि मूल्यसंच शोधा"),
    "fs-id1167836610583": ("MR-BRIDGE-009", "संबंध फलन आहे का ते ठरवा"),
    "fs-id1167824731607": ("MR-BRIDGE-010", "फलनाचे मूल्य काढा"),
    "fs-id1167829756260": ("MR-BRIDGE-007", "लेखी सराव"),
}
EXPECTED_SELECTION_COUNTS = (4, 4, 1, 16, 16, 31, 9, 21, 14, 18)


def text(node):
    return "".join(node.itertext()).strip()


def snapshot():
    with zipfile.ZipFile(ARCHIVE) as archive:
        raw = archive.read(MEMBER)
    if hashlib.sha256(raw).hexdigest() != MODULE_SHA:
        raise ValueError("canonical module hash drift")
    source = ET.fromstring(raw)
    source_ids = {n.get("id"): n for n in source.iter() if n.get("id")}
    parents = {child: node for node in source.iter() for child in node}
    roots, unit_hashes, selections, coverage, targets = {}, {}, defaultdict(list), defaultdict(list), defaultdict(list)
    by_unit = {}
    for unit in UNITS:
        unit_raw = (BASE / f"translations/{unit}.xml").read_bytes()
        root = ET.fromstring(unit_raw)
        roots[unit] = root
        unit_hashes[unit] = hashlib.sha256(unit_raw).hexdigest()
        current = []
        for node in root.iter():
            if node.get("id") in source_ids:
                targets[node.get("id")].append((unit, node))
            locator = node.get("data-source", "")
            if not locator.startswith("A20:m81373#"):
                continue
            sid = locator.split("#")[1]
            if sid not in source_ids or node.get("id") != sid:
                raise ValueError("unknown/mismatched selected source locator")
            selections[sid].append((unit, node))
            current.append(sid)
            for descendant in source_ids[sid].iter():
                coverage[descendant].append((unit, sid))
        selected_nodes = [n for sid in current for n in source_ids[sid].iter()]
        by_unit[unit] = {
            "selectors": len(current),
            "selected_original_ids": sum(bool(n.get("id")) for n in selected_nodes),
            "exercises": sum(n.tag == C + "exercise" for n in selected_nodes),
            "supplied_solutions": sum(n.tag == C + "solution" for n in selected_nodes),
            "ready_review_draft": unit in READY,
        }
    return source, source_ids, parents, roots, unit_hashes, selections, coverage, targets, by_unit


def public_report(data):
    source, source_ids, parents, roots, hashes, selections, coverage, targets, by_unit = data
    uncovered_text = []
    for node in source.iter():
        if node not in coverage and (node.text or "").strip():
            uncovered_text.append({"tag": node.tag, "id": node.get("id"),
                                   "parent_id": parents[node].get("id") if node in parents else None,
                                   "text": node.text.strip()})
    missing = [sid for sid in source_ids if sid not in targets]
    return {
        "scope": "m81373, units001-010; selection coverage is not completion",
        "module_sha256": MODULE_SHA,
        "unit_xml_sha256": hashes,
        "units": by_unit,
        "source_original_ids": len(source_ids),
        "selected_original_ids": sum(n.get("id") is not None for n in coverage),
        "represented_original_ids": len(targets),
        "missing_original_ids": missing,
        "missing_id_kinds": dict(Counter(source_ids[sid].tag.split("}")[-1] for sid in missing)),
        "unselected_original_ids": [sid for sid, n in source_ids.items() if n not in coverage],
        "unselected_text": uncovered_text,
        "duplicate_selectors": {sid: [u for u, _ in owners] for sid, owners in selections.items() if len(owners) > 1},
        "duplicate_selected_nodes": sum(len(owners) > 1 for owners in coverage.values()),
        "duplicate_original_targets": {sid: [u for u, _ in owners] for sid, owners in targets.items() if len(owners) > 1},
        "source_exercises": len(list(source.iter(C + "exercise"))),
        "source_supplied_solutions": len(list(source.iter(C + "solution"))),
        "source_links": [n.attrib for n in source.iter(C + "link")],
        "reader_qa_complete": False,
        "module_complete": False,
    }


class ModuleCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = snapshot()
        (cls.source, cls.source_ids, cls.parents, cls.roots, cls.hashes, cls.selections,
         cls.coverage, cls.targets, cls.by_unit) = cls.data

    def test_pinned_module_identity_includes_metadata_and_glossary(self):
        self.assertEqual(len(self.source_ids), 625)
        self.assertEqual(sum(bool(n.get("id")) for n in self.source.iter()), 625)
        self.assertEqual(text(self.source.find(C + "title")), "Relations and Functions")
        metadata = self.source.find(C + "metadata")
        self.assertEqual(text(metadata.find(MD + "content-id")), "m81373")
        self.assertEqual(text(metadata.find(MD + "uuid")), "59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20")
        self.assertEqual(len(list(self.source.find(C + "glossary"))), 5)

    def test_all_134_selectors_resolve_without_direct_or_nested_overlap(self):
        self.assertEqual(len(self.selections), 134)
        self.assertEqual(tuple(self.by_unit[u]["selectors"] for u in UNITS), EXPECTED_SELECTION_COUNTS)
        self.assertTrue(all(len(owners) == 1 for owners in self.selections.values()))
        self.assertTrue(all(len(owners) == 1 for owners in self.coverage.values()))
        self.assertTrue(all(len(owners) == 1 for owners in self.targets.values()))

    def test_unselected_text_is_only_known_titles_and_infrastructure(self):
        unselected_ids = {sid for sid, n in self.source_ids.items() if n not in self.coverage}
        self.assertEqual(unselected_ids, set(CONTEXTS) | MISSING_WRAPPERS)
        expected = Counter({
            "Relations and Functions": 2, "m81373": 1,
            "59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20": 1,
            "Find the Domain and Range of a Relation": 1,
            "Determine if a Relation is a Function": 1,
            "Find the Value of a Function": 1,
            "Practice Makes Perfect": 1, "Writing Exercises": 1,
        })
        actual = Counter((n.text or "").strip() for n in self.source.iter()
                         if n not in self.coverage and (n.text or "").strip())
        self.assertEqual(actual, expected)
        self.assertFalse(any((n.tail or "").strip() for n in self.source.iter()
                             if self.parents.get(n) not in self.coverage))

    def test_four_uncounted_context_ids_and_translated_headings_are_present(self):
        for sid, (unit, heading) in CONTEXTS.items():
            self.assertEqual(len(self.targets[sid]), 1)
            owner, node = self.targets[sid][0]
            self.assertEqual(owner, unit)
            self.assertIsNone(node.get("data-source"))
            self.assertEqual(text(node.find("h2")), heading)
        self.assertTrue(MISSING_WRAPPERS.isdisjoint(self.targets))

    def test_recorded_legacy_id_deficit_is_not_hidden_by_selected_parents(self):
        expected = {n.get("id") for sid in LEGACY_SELECTORS for n in self.source_ids[sid].iter()
                    if n.get("id") and n.get("id") != sid}
        self.assertEqual(len(expected), 61)
        self.assertEqual(set(self.source_ids) - set(self.targets), expected | MISSING_WRAPPERS)
        self.assertEqual(len(self.targets), 562)
        self.assertEqual(sum(bool(n.get("id")) for n in self.coverage), 619)
        for unit in UNITS[1:]:
            for sid, owners in self.selections.items():
                if owners[0][0] == unit:
                    local_ids = {n.get("id") for n in owners[0][1].iter()}
                    self.assertTrue({n.get("id") for n in self.source_ids[sid].iter() if n.get("id")} <= local_ids)

    def test_all_exercises_and_supplied_solutions_have_selected_owners(self):
        for tag, expected in (("exercise", 84), ("solution", 55)):
            nodes = list(self.source.iter(C + tag))
            self.assertEqual(len(nodes), expected)
            self.assertTrue(all(len(self.coverage[n]) == 1 for n in nodes))
            absent = [n for n in nodes if n.get("id") not in self.targets]
            self.assertEqual(len(absent), 3)
            self.assertTrue(all(self.coverage[n][0][0] == "MR-BRIDGE-001" for n in absent))
        self.assertEqual(sum(self.by_unit[u]["exercises"] for u in READY), 30)
        self.assertEqual(sum(self.by_unit[u]["supplied_solutions"] for u in READY), 18)
        unsupplied = [n for n in self.source.iter(C + "exercise") if n.find(C + "solution") is None]
        self.assertEqual(len(unsupplied), 29)
        target_ids = {n.get("id") for root in self.roots.values() for n in root.iter()}
        self.assertTrue(all("mr-answer-" + n.get("id") in target_ids for n in unsupplied))
        authored = {n.get("id"): n for root in self.roots.values() for n in root.iter() if n.get("id")}
        self.assertTrue(all(authored["mr-answer-" + n.get("id")].get("data-kind") == "original" for n in unsupplied))

    def test_objectives_readiness_key_concepts_self_check_and_glossary_are_located(self):
        for sid in ("para-00001", "list-00001", "fs-id1167836299681", "fs-idm404421072", "fs-idm387231616"):
            self.assertEqual(self.selections[sid][0][0], "MR-BRIDGE-008")
        self.assertEqual(len(self.source_ids["list-00001"].findall(C + "item")), 3)
        self.assertEqual(self.selections["fs-id1167829711772"][0][0], "MR-BRIDGE-003")
        self.assertEqual(self.selections["fs-id1167829783756"][0][0], "MR-BRIDGE-007")
        glossary = list(self.source.find(C + "glossary"))
        self.assertEqual(Counter(self.selections[n.get("id")][0][0] for n in glossary),
                         {"MR-BRIDGE-007": 4, "MR-BRIDGE-001": 1})

    def test_all_seven_source_links_retained_with_external_limits_explicit(self):
        links = list(self.source.iter(C + "link"))
        self.assertEqual(len(links), 7)
        expected_links = Counter((self.coverage[n][0][0], n.get("document", "m81373"),
                                  n.get("target-id"), n.get("url")) for n in links)
        actual_links = Counter()
        all_target_ids = {n.get("id") for root in self.roots.values() for n in root.iter()}
        for unit, root in self.roots.items():
            for anchor in root.iter("a"):
                if anchor.get("data-source-document"):
                    actual_links[(unit, anchor.get("data-source-document"), anchor.get("data-source-target-id"), None)] += 1
                elif anchor.get("href") == "https://openstax.org/l/37introfunction":
                    actual_links[(unit, "m81373", None, anchor.get("href"))] += 1
        self.assertEqual(actual_links, expected_links)
        for source_link in links:
            unit, unused_selector = self.coverage[source_link][0]
            target_id = source_link.get("target-id")
            if source_link.get("url"):
                actual = [a for a in self.roots[unit].iter("a") if a.get("href") == source_link.get("url")]
            else:
                document = source_link.get("document", "m81373")
                actual = [a for a in self.roots[unit].iter("a") if a.get("data-source-target-id") == target_id
                          and a.get("data-source-document") == document]
                if document == "m81373":
                    self.assertEqual(self.targets[target_id][0][0], "MR-BRIDGE-008")
                else:
                    self.assertEqual(document, "m81422")
                    self.assertNotIn(target_id, all_target_ids)
            self.assertTrue(actual)
            self.assertTrue(all(a.get("href", "").startswith("https://") and text(a) for a in actual))
        for unit, root in self.roots.items():
            ids = {n.get("id") for n in root.iter()}
            for anchor in root.iter("a"):
                if anchor.get("href", "").startswith("#"):
                    self.assertIn(anchor.get("href")[1:], ids, (unit, anchor.attrib))

    def test_ready_units_are_not_inferred_from_draft_coverage(self):
        self.assertEqual(sum(self.by_unit[u]["selectors"] for u in READY), 41)
        self.assertEqual(sum(self.by_unit[u]["selectors"] for u in UNITS[5:]), 93)
        report = public_report(self.data)
        self.assertFalse(report["module_complete"])
        self.assertFalse(report["reader_qa_complete"])


if __name__ == "__main__":
    if sys.argv[1:] == ["--report"]:
        print(json.dumps(public_report(snapshot()), ensure_ascii=False, indent=2))
    else:
        unittest.main(verbosity=2)
