"""Independent complete-source union audit for the nine m49301 excerpts.

No renderer or preparer is imported. Match every source element, including
ID-less prose/MathML leaves, attributes, text and tails, to its canonical path.
This establishes source selection coverage, not linguistic or visual approval.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
SOURCE = ROOT / "downloads/m49301.cnxml"
PIN = "81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3"
NAMES = ["m49301-opening.cnxml", "m49301-menu.cnxml", "m49301-unit-003.cnxml",
         "m49301-unit-004.cnxml"] + [f"unit-{n:03d}.cnxml" for n in range(5, 10)]
BOUNDARY_TAILS = {
    ("PNB-003", (2, 1, 14)): ("\n", None),
    ("PNB-003", (2, 1, 15)): ("\n\n", None),
    ("PNB-004", (2, 1, 16)): ("\n", None),
    ("PNB-005", (2, 1, 17)): (None, "\n"),
    ("PNB-006", (2, 2)): ("\n\n ", None),
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(node):
    return node.tag.rsplit("}", 1)[-1]


def shallow(node):
    return node.tag, sorted(node.attrib.items()), node.text, node.tail


def signature(node):
    return shallow(node), tuple(signature(child) for child in node)


def audit(full, excerpts):
    indexed, paths = {}, {}
    assert full.attrib == {} and not (full.text or "").strip() and full.tail is None

    def index(node, path):
        paths[node] = path
        if node.get("id"):
            assert node.get("id") not in indexed, "duplicate canonical ID"
            indexed[node.get("id")] = node
        for number, child in enumerate(node):
            index(child, path + (number,))

    index(full, ())
    seen, owners, roots, boundary_whitespace = Counter(), {}, [], []

    def match(selected, original, unit, selection_root=False):
        if shallow(selected) != shallow(original):
            # Older excerpts detached or added selected-root formatting tails.
            # Permit only those witnessed formatting differences, never prose,
            # internal spacing, mathematical spacing or a non-root tail.
            assert selection_root and not (selected.tail or "").strip() \
                and not (original.tail or "").strip() and shallow(selected)[:3] == shallow(original)[:3], \
                f"source content changed: {unit}:{paths[original]}"
            assert BOUNDARY_TAILS.get((unit, paths[original])) == (original.tail, selected.tail), \
                "unlisted selection-root whitespace difference"
            boundary_whitespace.append({"unit": unit, "path": list(paths[original]),
                                        "canonical_tail": original.tail, "excerpt_tail": selected.tail})
        path = paths[original]
        seen[path] += 1
        owners[path] = unit
        cursor = 0
        for child in selected:
            candidates = [(i, node) for i, node in enumerate(original) if i >= cursor
                          and (node.get("id") == child.get("id") if child.get("id")
                               else signature(node) == signature(child))]
            assert candidates, f"missing/reordered child: {unit}:{path}"
            # An ID-less partial container occurs only at the excerpt root,
            # where it is located independently below. Other ID-less trees
            # must be complete source subtrees, including repeated math leaves.
            i, node = candidates[0]
            match(child, node, unit)
            cursor = i + 1

    for number, excerpt in enumerate(excerpts, 1):
        unit = f"PNB-{number:03d}"
        unit_roots = []
        for selected in excerpt:
            if selected.get("id"):
                original = indexed[selected.get("id")]
            else:
                candidates = [node for node in full if node.tag == selected.tag]
                assert len(candidates) == 1, "ambiguous root-level ID-less container"
                original = candidates[0]
            unit_roots.append(paths[original])
            match(selected, original, unit, selection_root=True)
        assert unit_roots == sorted(unit_roots), f"source selection order changed: {unit}"
        roots.append({"unit": unit, "canonical_root_paths": [list(p) for p in unit_roots]})

    expected = set(paths.values()) - {()}
    assert set(seen) == expected, f"uncovered source nodes: {sorted(expected-set(seen))[:20]}"
    assert all(n == 1 for n in seen.values()), "source nodes duplicated between excerpts"
    ids = [node.get("id") for node in paths if node.get("id")]
    math = [node for node in paths if node.tag == "{http://www.w3.org/1998/Math/MathML}math"]
    media = [node for node in paths if local(node) == "media"]
    ledger = [{"path": list(paths[node]), "tag": node.tag, "id": node.get("id"),
               "unit": owners[paths[node]],
               "shallow_sha256": digest(json.dumps(shallow(node), ensure_ascii=False,
                                                     separators=(",", ":")).encode())}
              for node in paths if node is not full]
    return {"source_elements_excluding_document": len(expected), "source_ids": len(ids),
            "source_mathml_trees": len(math), "source_media": len(media),
            "element_counts": dict(sorted(Counter(local(n) for n in paths if n is not full).items())),
            "per_unit_elements": dict(sorted(Counter(owners.values()).items())),
            "selection_roots": roots, "detached_selection_root_whitespace": boundary_whitespace, "ledger": ledger}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    raw = SOURCE.read_bytes().replace(b"\r\n", b"\n")
    assert digest(raw) == PIN, "canonical source pin mismatch"
    full = ET.fromstring(raw)
    raw_excerpts = [(BASE / "source-excerpts" / name).read_bytes() for name in NAMES]
    excerpts = [ET.fromstring(raw) for raw in raw_excerpts]
    result = audit(full, excerpts)
    assert result["source_ids"] == 805 and result["source_mathml_trees"] == 411
    # Detached mutations prove omissions, altered ID-less wording, math and
    # source order fail independently of the retained-ID totals.
    mutations = []
    for label, mutate in [
        ("omit_objective_without_id", lambda e: e[8].find(".//{http://cnx.rice.edu/cnxml}list").remove(
            e[8].find(".//{http://cnx.rice.edu/cnxml}list")[0])),
        ("change_idless_glossary_term", lambda e: setattr(e[8].find(".//{http://cnx.rice.edu/cnxml}term"), "text", "changed")),
        ("change_idless_math_leaf", lambda e: setattr(e[8].find(".//{http://www.w3.org/1998/Math/MathML}mi"), "text", "changed")),
        ("alter_math_attribute", lambda e: e[8].find(".//{http://www.w3.org/1998/Math/MathML}math").set("display", "changed")),
        ("alter_internal_tail", lambda e: setattr(e[8].find(".//{http://cnx.rice.edu/cnxml}term"), "tail", "changed")),
        ("add_new_boundary_whitespace_exception", lambda e: setattr(e[7][0], "tail", "\n\n\n")),
        ("omit_whole_exercise", lambda e: next(n for n in e[8].iter() if any(local(c) == "exercise" for c in n)).remove(
            next(n for n in e[8].iter() if local(n) == "exercise"))),
        ("duplicate_excerpt", lambda e: e.append(copy.deepcopy(e[0]))),
        ("reverse_top_level_order", lambda e: e[7].__setitem__(slice(None), list(reversed(e[7])))),
    ]:
        detached = copy.deepcopy(excerpts)
        mutate(detached)
        try:
            audit(full, detached)
        except (AssertionError, KeyError):
            mutations.append(label)
        else:
            raise AssertionError("mutation survived: " + label)
    report = {"module": "m49301", "canonical_commit": "789b54099106b071d1d32bfcee454fed72eb4768",
              "canonical_lf_sha256": PIN, "status": "complete_source_selection_union_pass",
              "method": "Canonical path union, with every non-document element represented exactly once; tag, attributes, text, tail and ordered child selection checked, including ID-less nodes. Only five explicitly allowlisted whitespace-only tail differences at selected roots are accepted; internal text/tails remain exact. Synthetic excerpt wrappers excluded.",
              "limitations": "Source coverage only. Use each reader's independent QA and bounded visual review before counting the module complete. No native-speaker, educator or assistive-technology certification. Nine reader order differs from source root order because metadata/glossary are backfilled in PNB009.",
              "script_sha256": digest(Path(__file__).read_bytes()),
              "excerpt_sha256": {name: digest(raw.replace(b"\r\n", b"\n")) for name, raw in zip(NAMES, raw_excerpts)},
              "detached_mutations_rejected": mutations, **result}
    output = BASE / "qa/m49301-source-coverage.json"
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.check_only:
        assert output.read_text(encoding="utf-8") == rendered, "coverage receipt is stale"
    else:
        output.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "ledger"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
