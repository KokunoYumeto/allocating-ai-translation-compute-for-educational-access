"""Read-only structural coverage audit of the pinned m49301 pedagogical scope.

Print JSON; write no files, run no builders/checkers and fetch nothing. Registered
excerpts are not accepted readers unless current canon/build/visual receipts bind
their actual bytes. Missing direct MathML capture is NOT automatically semantic
loss: exact XML and nearby draft context are reported for individual review.
This tool does not make the judgment approving rendered equivalents or prove translation meaning,
mathematical truth, native fluency, or completion of a module/book/assignment.

Optional provenance/m49301-rendered-equivalents.json schema:
{"schema":1,"module":"m49301","source_module_sha256":"...",
 "entries":[{"unit":"A30-U001","source_math_key":"owner:0",
 "source_math_sha256":"SHA of the gap's exact source_mathml UTF-8 string",
 "translation_sha256":"...","reader_sha256":"...",
 "review_status":"approved_equivalent","reviewer":"root",
 "draft_snippets":["exact current draft text"],
 "rendered_snippets":["exact current HTML text"],"rationale":"individual reason"}]}
The audit verifies these bindings, not the reviewer's substantive judgment.
"""
import sys
# No bytecode writes, including when CLI is invoked without Python's -B option.
sys.dont_write_bytecode = True
import argparse
import base64
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from build import Inspector, prune_empty_math_layout, validate_reader_links

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"
SOURCE_SHA = "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612"
CN = "http://cnx.rice.edu/cnxml"
MD = "http://cnx.rice.edu/mdml"
MATH = "http://www.w3.org/1998/Math/MathML"
EXERCISES_ID = "fs-id1165137737761"
PLACEHOLDER = re.compile(r"\{\{math:([^:}]+):(\d+)\}\}")
ANCHOR = re.compile(r"\{#([^\s}]+)(?:\s+[^}]*)?\}")


def digest(data):
    return sha256(data).hexdigest()


def local(tag):
    return tag.rsplit("}", 1)[-1]


def normalized(text):
    return " ".join((text or "").split())


def canonical_math(node):
    """Ignore indentation/prefixes and HTML mtext wrapping, not math structure."""
    return (local(node.tag),
            tuple(sorted((k, v) for k, v in node.attrib.items()
                         if k not in ("data-source", "xmlns"))),
            normalized(node.text) if local(node.tag) == "mtext" else (node.text or "").strip(),
            tuple((canonical_math(child), (child.tail or "").strip()) for child in node))


def source_math_bytes(node):
    """Match the builder's default ns0 serialization without global prefix state."""
    def copy_prefixed(original, top=False):
        copied = ET.Element("ns0:" + local(original.tag))
        if top:
            copied.set("xmlns:ns0", MATH)
        for key, value in original.attrib.items():
            if key.startswith("{http://www.w3.org/XML/1998/namespace}"):
                key = "xml:" + local(key)
            elif key.startswith("{"):
                raise ValueError(f"unsupported source MathML attribute namespace: {key}")
            copied.set(key, value)
        copied.text = original.text
        copied.tail = None if top else original.tail
        copied.extend(copy_prefixed(child) for child in original)
        return copied
    return ET.tostring(copy_prefixed(node, top=True))


class Inventory:
    """ID-relative content atoms also catch anonymous list items/table entries."""
    def __init__(self, roots):
        self.ids, self.atoms, self.math, self.math_keys = {}, {}, {}, {}
        self.parents, self.duplicates, self.nodekeys = {}, [], {}
        occurrences = Counter()

        def walk(node, owner=None, key=None):
            identity = node.get("id")
            if identity:
                owner, key = identity, "id:" + identity
                if identity in self.ids:
                    self.duplicates.append(identity)
                self.ids[identity] = node
            if node.tag == f"{{{MATH}}}math":
                if owner is None:
                    raise ValueError("source MathML has no source-ID owner")
                math_key = f"{owner}:{occurrences[owner]}"
                occurrences[owner] += 1
                self.math[math_key] = node
                self.math_keys[node] = math_key
                return
            if owner is not None:
                self.nodekeys[node] = key
                self.atoms[key] = {
                    "tag": node.tag,
                    "attributes": {k: v for k, v in node.attrib.items() if k != "id"},
                    "text": normalized(node.text),
                }
            anonymous = Counter()
            for child in node:
                self.parents[child] = node
                if child.get("id"):
                    child_key = "id:" + child.get("id")
                else:
                    anonymous[child.tag] += 1
                    child_key = f"{key}/{local(child.tag)}[{anonymous[child.tag]}]"
                walk(child, owner, child_key)
                if owner is not None and normalized(child.tail):
                    self.atoms[child_key + "#tail"] = {"text": normalized(child.tail)}

        for root in roots:
            walk(root)


def pedagogical_roots(document):
    roots = [document.find(f".//{{{MD}}}abstract"),
             document.find(f"{{{CN}}}content"), document.find(f"{{{CN}}}glossary")]
    if any(root is None for root in roots):
        raise ValueError("full source must contain metadata abstract, content and glossary")
    return roots


def relative_file(root, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("missing local relative path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError(f"path outside language package: {relative}")
    return path


def audit(root=ROOT, source=SOURCE, expected_source_sha=SOURCE_SHA):
    root, source = Path(root).resolve(), Path(source).resolve()
    snapshots = {}
    changed_reads = set()
    report = {
        "schema": 1, "module": "m49301", "mode": "read_only_no_network_no_build",
        "result": "incomplete_or_unverified", "issues": [], "units": {},
        "limits": [
            "Structural coverage is not proof of translation semantics, mathematical correctness or native fluency.",
            "Direct source MathML, source-excerpt retention and accepted reader coverage are distinct measures.",
            "Manual mathematical restatements are not approved or rejected semantically by this audit.",
            "Only registered units with current accepted canon/build/visual receipts count as accepted readers.",
            "No module/book/whole-assignment completion status is set by this tool.",
        ],
    }

    def remember(path, value):
        path = Path(path).resolve()
        if path in snapshots and snapshots[path] != value:
            changed_reads.add(path)
        snapshots.setdefault(path, value)

    def read(path):
        path = Path(path).resolve()
        data = path.read_bytes()
        remember(path, digest(data))
        return data

    def load(path):
        return json.loads(read(path).decode("utf-8"))

    def issue(code, detail, unit=None):
        entry = {"code": code, "detail": detail}
        if unit:
            entry["unit"] = unit
        report["issues"].append(entry)

    try:
        source_data = read(source)
        report["source"] = {"path": str(source), "sha256": digest(source_data),
                            "expected_sha256": expected_source_sha}
        if digest(source_data) != expected_source_sha:
            raise ValueError("pinned full-source SHA256 mismatch")
        document = ET.fromstring(source_data)
        full = Inventory(pedagogical_roots(document))
        if full.duplicates:
            raise ValueError(f"duplicate full-source IDs: {full.duplicates}")
        configs = load(root / "units.json")
        if not isinstance(configs, dict):
            raise ValueError("unit registry must be an object")
        report["registry_sha256"] = snapshots[root / "units.json"]
    except (OSError, ValueError, ET.ParseError) as error:
        issue("input_error", str(error))
        report["result"] = "integrity_errors"
        return report

    admitted = defaultdict(set)
    for path in sorted((root / "provenance").glob("*asset-notice*.json")):
        try:
            entries = load(path)
            if isinstance(entries, list):
                for row in entries:
                    if row.get("admission") == "admitted" and row.get("sha256"):
                        admitted[Path(row["asset_path"]).name].add(row["sha256"])
        except (OSError, ValueError, KeyError, TypeError) as error:
            issue("asset_notice_error", f"{path.name}: {error}")

    excerpt_owners, accepted_owners = defaultdict(set), defaultdict(set)
    excerpt_atoms, accepted_atoms = defaultdict(set), defaultdict(set)
    excerpt_math, direct_math, equivalent_math = defaultdict(set), defaultdict(set), defaultdict(set)
    ledger_entries = defaultdict(list)
    ledger_path = root / "provenance/m49301-rendered-equivalents.json"
    report["equivalence_ledger"] = {
        "path": str(ledger_path), "present": ledger_path.is_file(),
        "basis": "Recorded reviewer judgment plus verified exact source/draft/reader bindings; not automated semantic proof.",
    }
    if ledger_path.is_file():
        try:
            ledger = load(ledger_path)
            if (ledger.get("schema") != 1 or ledger.get("module") != "m49301"
                    or ledger.get("source_module_sha256") != digest(source_data)
                    or not isinstance(ledger.get("entries"), list)):
                raise ValueError("ledger schema/module/full-source binding mismatch")
            seen = set()
            for entry in ledger["entries"]:
                key = (entry["unit"], entry["source_math_key"])
                if key in seen:
                    raise ValueError(f"duplicate equivalent review entry: {key}")
                seen.add(key)
                if entry["unit"] not in configs:
                    raise ValueError(f"unregistered equivalent-review unit: {entry['unit']}")
                ledger_entries[entry["unit"]].append(entry)
            report["equivalence_ledger"]["entries"] = len(seen)
            report["equivalence_ledger"]["sha256"] = snapshots[ledger_path]
        except (OSError, ValueError, KeyError, TypeError) as error:
            issue("equivalence_ledger_error", str(error))
            ledger_entries.clear()
    source_assets = {Path(n.get("src")).name for n in document.iter(f"{{{CN}}}image")}
    accepted_assets = defaultdict(set)
    for unit, config in configs.items():
        if not unit.startswith("A30-") or "m49301" not in config.get("source", ""):
            continue
        start_issues = len(report["issues"])
        unit_report = {"accepted_receipts": False, "direct_math_capture_gaps": [],
                       "verified_reviewed_equivalent_keys": [],
                       "technical_anchor_aliases": [], "source_content_mismatches": [],
                       "source_math_mismatches": []}
        report["units"][unit] = unit_report
        try:
            source_path = relative_file(root, config["source"])
            draft_path = relative_file(root, f"translation/{config['slug']}.vi.md")
            reader_path = relative_file(root, f"review/{config['slug']}.vi.html")
            excerpt_data, draft_data = read(source_path), read(draft_path)
            excerpt = Inventory([ET.fromstring(excerpt_data)])
            draft = draft_data.decode("utf-8")
            raw_draft = Inspector()
            raw_draft.feed(draft)
            anchors = Counter(ANCHOR.findall(draft)) + Counter(raw_draft.ids)
            unit_report.update({
                "source_excerpt_sha256": digest(excerpt_data),
                "translation_sha256": digest(draft_data),
                "excerpt_source_ids": len(excerpt.ids),
                "excerpt_source_mathml": len(excerpt.math),
                "explicit_source_anchors": len(set(anchors) & set(full.ids)),
            })
            if excerpt.duplicates:
                issue("duplicate_excerpt_id", excerpt.duplicates, unit)
            if any(count != 1 for count in anchors.values()):
                issue("duplicate_draft_anchor", [k for k, n in anchors.items() if n != 1], unit)
            for identity, node in excerpt.ids.items():
                if identity not in full.ids:
                    issue("unknown_excerpt_id", identity, unit)
                elif node.tag != full.ids[identity].tag:
                    issue("source_tag_mismatch", identity, unit)
                else:
                    excerpt_owners[identity].add(unit)
            for key, atom in excerpt.atoms.items():
                if key in full.atoms and atom == full.atoms[key]:
                    excerpt_atoms[key].add(unit)
                else:
                    mismatch = {"key": key, "expected": full.atoms.get(key), "actual": atom}
                    unit_report["source_content_mismatches"].append(mismatch)
            if unit_report["source_content_mismatches"]:
                issue("source_content_mismatch",
                      len(unit_report["source_content_mismatches"]), unit)
            for key, math in excerpt.math.items():
                if key in full.math and canonical_math(math) == canonical_math(full.math[key]):
                    excerpt_math[key].add(unit)
                else:
                    unit_report["source_math_mismatches"].append(key)
            if unit_report["source_math_mismatches"]:
                issue("source_math_mismatch", unit_report["source_math_mismatches"], unit)

            placeholder_refs, inserted_keys, inserted_nodes = [], [], []
            for identity, raw_index in PLACEHOLDER.findall(draft):
                node = excerpt.ids[identity]
                math = list(node.iter(f"{{{MATH}}}math"))[int(raw_index)]
                placeholder_refs.append(f"{identity}:{raw_index}")
                inserted_keys.append(excerpt.math_keys[math])
                inserted_nodes.append(math)
            if "{{math:" in PLACEHOLDER.sub("", draft):
                issue("malformed_math_placeholder", "unresolved syntax", unit)
            repeated = [key for key, count in Counter(inserted_keys).items() if count > 1]
            if repeated:
                issue("duplicate_math_capture", repeated, unit)
            for key in sorted(set(excerpt.math) - set(inserted_keys)):
                math = excerpt.math[key]
                owner = math
                while owner is not None and owner.get("id") not in anchors:
                    owner = excerpt.parents.get(owner)
                anchor = owner.get("id") if owner is not None else None
                position = draft.find("{#" + anchor) if anchor else 0
                if anchor and position < 0:
                    position = draft.find('id="' + anchor + '"')
                unit_report["direct_math_capture_gaps"].append({
                    "source_math_key": key,
                    "source_mathml": source_math_bytes(full.math.get(key, math)).decode("utf-8"),
                    "source_math_sha256": digest(source_math_bytes(full.math.get(key, math))),
                    "source_text": normalized("".join(math.itertext())),
                    "nearest_draft_anchor": anchor,
                    "draft_line": draft[:position].count("\n") + 1,
                    "draft_context": draft[max(0, position - 120):position + 1100],
                    "rendered_equivalence": "not_assessed_requires_individual_review",
                })
            unit_report["direct_placeholder_count"] = len(placeholder_refs)

            # A current receipt is necessary, not a semantic proof.
            canon = load(root / f"canon/review-{unit}.json")
            build = load(root / f"qa/build-{unit}.json")
            visual_path = relative_file(root, config["visual_receipt"])
            visual = load(visual_path)
            reader_data = read(reader_path)
            reader = reader_data.decode("utf-8")
            inspector = Inspector()
            inspector.feed(reader)
            html_ids = Counter(inspector.ids)
            for kind, receipt in (("canon", canon), ("build", build), ("visual", visual)):
                if receipt.get("unit") != unit:
                    issue("receipt_unit_mismatch", kind, unit)
            if not canon.get("draft_checked") or not canon.get("final_checked"):
                issue("canon_not_accepted", "draft_checked/final_checked", unit)
            if len(set(canon.get("examples_consulted", []))) < config.get("minimum_canon_examples", 1):
                issue("canon_examples_missing", "minimum consulted examples not recorded", unit)
            for kind, receipt in (("canon", canon), ("build", build)):
                if receipt.get("translation_sha256") != digest(draft_data):
                    issue("receipt_draft_hash_mismatch", kind, unit)
            if canon.get("source_excerpt_sha256", digest(excerpt_data)) != digest(excerpt_data):
                issue("canon_source_hash_mismatch", "excerpt changed", unit)
            if build.get("source_excerpt_sha256") != digest(excerpt_data):
                issue("build_source_hash_mismatch", "excerpt changed", unit)
            for kind, receipt in (("build", build), ("visual", visual)):
                if receipt.get("result") != "pass":
                    issue("receipt_not_pass", kind, unit)
                if receipt.get("html_sha256") != digest(reader_data):
                    issue("receipt_reader_hash_mismatch", kind, unit)
            if build.get("canon_review") != f"canon/review-{unit}.json":
                issue("build_canon_path_mismatch", build.get("canon_review"), unit)
            if build.get("visual_review") != config["visual_receipt"]:
                issue("build_visual_path_mismatch", build.get("visual_review"), unit)
            aliases = {row["source_id"]: row["translated_block"]
                       for row in build.get("technical_anchor_aliases", [])}
            unit_report["technical_anchor_aliases"] = list(aliases)
            for identity in excerpt.ids:
                if html_ids[identity] != 1:
                    issue("reader_source_anchor_missing_or_duplicate", identity, unit)
                if anchors[identity] != 1:
                    parent = aliases.get(identity)
                    if not parent or anchors[parent] != 1 or html_ids[parent] != 1:
                        issue("draft_source_anchor_missing", identity, unit)
                    else:
                        ancestor = excerpt.parents.get(excerpt.ids[identity])
                        while ancestor is not None and ancestor.get("id") != parent:
                            ancestor = excerpt.parents.get(ancestor)
                        if ancestor is None:
                            issue("invalid_technical_alias_parent", identity, unit)
            if any(count != 1 for count in html_ids.values()):
                issue("reader_duplicate_ids", "duplicate rendered anchors", unit)
            insertion_rows = build.get("source_math_insertions", [])
            recorded_refs = [f"{row['source_id']}:{row['math_index']}" for row in insertion_rows]
            if Counter(recorded_refs) != Counter(placeholder_refs):
                issue("build_math_receipt_mismatch", "placeholder occurrence inventory", unit)
            if Counter(inspector.source_math) != Counter(placeholder_refs):
                issue("reader_math_capture_mismatch", "data-source occurrence inventory", unit)
            for row in insertion_rows:
                math = list(excerpt.ids[row["source_id"]].iter(f"{{{MATH}}}math"))[row["math_index"]]
                if row.get("source_math_sha256") != digest(source_math_bytes(math)):
                    issue("build_math_hash_mismatch", f"{row['source_id']}:{row['math_index']}", unit)
            rendered_math = {}
            for fragment in re.findall(r"<math\b[^>]*>.*?</math>", reader, re.S):
                try:
                    node = ET.fromstring(fragment)
                except ET.ParseError as error:
                    reference = re.search(r'data-source="([^"]+)"', fragment)
                    if reference:
                        issue("reader_math_xml_boundary",
                              {"reference": reference[1], "error": str(error),
                               "raw_fragment": fragment,
                               "meaning": "Raw MathML boundary is not XML-balanced; browser repair/semantic effect not inferred."},
                              unit)
                    continue
                if node.get("data-source"):
                    rendered_math[node.get("data-source")] = node
            for reference, math in zip(placeholder_refs, inserted_nodes):
                expected = deepcopy(math)
                for element in expected.iter():
                    element.tag = local(element.tag)
                    if local(element.tag) == "mtext" and element.text:
                        for old, new in config.get("math_text", {}).items():
                            element.text = element.text.replace(old, new)
                if config.get("prune_empty_math_layout"):
                    prune_empty_math_layout(expected)
                actual = rendered_math.get(reference)
                if actual is None or canonical_math(actual) != canonical_math(expected):
                    issue("rendered_source_math_mismatch", reference, unit)
            if re.search(r"&lt;/?(?:math|mrow|mfrac|msqrt|mtable)\b", reader):
                issue("escaped_mathml", "source markup displayed as code", unit)
            links = validate_reader_links(inspector.links, inspector.ids, root / "review", configs)
            for link in links["cross_reader_links"]:
                target = root / "review" / link["target_reader"]
                remember(target, link["target_sha256"])
                read(target)  # Bind the helper's read and our ending snapshot.
            if links["cross_reader_links"] != build.get("cross_reader_links", []):
                issue("cross_reader_receipt_mismatch", "current target anchors/bytes differ", unit)

            embedded = []
            for image in inspector.images:
                src = image.get("src", "")
                if not image.get("alt") or not re.match(r"data:image/[^;,]+;base64,", src):
                    issue("reader_image_not_embedded_or_described", src[:80], unit)
                else:
                    embedded.append(digest(base64.b64decode(src.split(",", 1)[1], validate=True)))
            unit_assets = set()
            images = [atom for atom in excerpt.atoms.values()
                      if atom.get("tag") == f"{{{CN}}}image"]
            for image in images:
                name = Path(image["attributes"]["src"]).name
                asset = read(relative_file(root, "assets/" + name))
                asset_sha = digest(asset)
                if asset_sha not in admitted[name]:
                    issue("source_asset_admitted_hash_missing", name, unit)
                if asset_sha not in embedded:
                    issue("source_asset_not_rendered", name, unit)
                unit_assets.add(name)
            # New supplementary plots and reused source images also stay byte-bound.
            for relative in re.findall(r"!\[[^\n]*?\]\(([^)\s]+)\)", draft):
                path = (draft_path.parent / relative).resolve()
                if not path.is_relative_to(root):
                    issue("draft_image_outside_package", relative, unit)
                    continue
                data = read(path)
                if digest(data) not in embedded:
                    issue("draft_image_not_rendered", relative, unit)
                if path.name in source_assets and digest(data) not in admitted[path.name]:
                    issue("source_asset_admitted_hash_missing", path.name, unit)
            if len(embedded) != config.get("images"):
                issue("reader_image_count_mismatch", len(embedded), unit)
            for entry in ledger_entries[unit]:
                key = entry["source_math_key"]
                problems = []
                if key not in excerpt.math or key not in full.math:
                    problems.append("source math key is not owned by this unit")
                elif entry.get("source_math_sha256") != digest(source_math_bytes(full.math[key])):
                    problems.append("original serialized source MathML hash mismatch")
                if entry.get("translation_sha256") != digest(draft_data):
                    problems.append("draft hash mismatch")
                if entry.get("reader_sha256") != digest(reader_data):
                    problems.append("reader hash mismatch")
                if (entry.get("review_status") != "approved_equivalent"
                        or not isinstance(entry.get("reviewer"), str)
                        or not entry["reviewer"].strip()
                        or not isinstance(entry.get("rationale"), str)
                        or not entry["rationale"].strip()):
                    problems.append("missing individual reviewer approval/rationale")
                for field, text in (("draft_snippets", draft), ("rendered_snippets", reader)):
                    snippets = entry.get(field)
                    if (not isinstance(snippets, list) or not snippets
                            or not all(isinstance(s, str) and s.strip() and s in text for s in snippets)):
                        problems.append(f"{field} must contain exact nonempty current snippets")
                if problems:
                    issue("equivalent_review_binding_error", {"key": key, "problems": problems}, unit)
                else:
                    unit_report["verified_reviewed_equivalent_keys"].append(key)
                    for gap in unit_report["direct_math_capture_gaps"]:
                        if gap["source_math_key"] == key:
                            gap["rendered_equivalence"] = "recorded_reviewer_approval_with_verified_bindings"
                            gap["reviewer"] = entry["reviewer"]
                            gap["review_rationale"] = entry["rationale"]
            unit_report["accepted_receipts"] = len(report["issues"]) == start_issues
            unit_report["reader_sha256"] = digest(reader_data)
            unit_report["source_assets"] = sorted(unit_assets)
            unit_report["external_links_unverified"] = links["external_links"]
            if unit_report["accepted_receipts"]:
                for identity in set(excerpt.ids) & set(full.ids):
                    accepted_owners[identity].add(unit)
                for key in excerpt.atoms:
                    if unit in excerpt_atoms[key]:
                        accepted_atoms[key].add(unit)
                for key in inserted_keys:
                    if unit in excerpt_math[key]:
                        direct_math[key].add(unit)
                for key in unit_report["verified_reviewed_equivalent_keys"]:
                    if unit in excerpt_math[key]:
                        equivalent_math[key].add(unit)
                for name in unit_assets:
                    accepted_assets[name].add(unit)
        except (OSError, ValueError, KeyError, IndexError, TypeError, ET.ParseError, AssertionError) as error:
            issue("unit_input_or_integrity_error", str(error), unit)
        unit_report["issue_count"] = len(report["issues"]) - start_issues

    def ancestors(node):
        while node in full.parents:
            node = full.parents[node]
            yield node

    groups = {
        "end_exercises": [identity for identity, node in full.ids.items()
                          if local(node.tag) == "exercise"
                          and any(a.get("id") == EXERCISES_ID for a in ancestors(node))],
        "examples": [identity for identity, node in full.ids.items() if local(node.tag) == "example"],
        "try_it_exercises": [identity for identity, node in full.ids.items()
                             if local(node.tag) == "exercise" and
                             any("try" in a.get("class", "").split() for a in ancestors(node))],
        "glossary_definitions": [identity for identity, node in full.ids.items()
                                 if local(node.tag) == "definition"],
    }
    report["counts"] = {}
    for label, identities in groups.items():
        report["counts"][label] = {
            "original": len(identities),
            "registered_excerpt_unique": sum(bool(excerpt_owners[x]) for x in identities),
            "accepted_reader_unique": sum(bool(accepted_owners[x]) for x in identities),
            "accepted_occurrences": sum(len(accepted_owners[x]) for x in identities),
            "missing_accepted_ids": [x for x in identities if not accepted_owners[x]],
            "duplicate_accepted_ids": {x: sorted(accepted_owners[x]) for x in identities
                                       if len(accepted_owners[x]) > 1},
        }
    abstract = document.find(f".//{{{MD}}}abstract")
    objective_nodes = list(abstract.iter(f"{{{CN}}}item"))
    objective_keys = [full.nodekeys[node] for node in objective_nodes]
    report["counts"]["learning_objectives"] = {
        "original": len(objective_nodes),
        "accepted": sum(bool(accepted_atoms[k]) for k in objective_keys),
        "missing": [full.atoms[k]["text"] for k in objective_keys if not accepted_atoms[k]],
    }
    preserved_math = {key: direct_math[key] | equivalent_math[key] for key in full.math}
    report["coverage"] = {}
    for label, originals, registered, accepted in (
        ("source_ids", full.ids, excerpt_owners, accepted_owners),
        ("content_atoms", full.atoms, excerpt_atoms, accepted_atoms),
        ("source_mathml", full.math, excerpt_math, preserved_math),
    ):
        report["coverage"][label] = {
            "original": len(originals),
            "registered_excerpt_unique": sum(bool(registered[k]) for k in originals),
            "accepted_unique": sum(bool(accepted[k]) for k in originals),
            "missing_from_registered_excerpts": [k for k in originals if not registered[k]],
            "missing_from_accepted_readers": [k for k in originals if not accepted[k]],
        }
    report["coverage"]["source_mathml"].update({
        "accepted_measure": "Direct captures plus individually reviewed equivalents whose current bindings/snippets verify; no automated semantic approval.",
        "accepted_direct_unique": sum(bool(direct_math[k]) for k in full.math),
        "accepted_reviewed_equivalent_unique": sum(bool(equivalent_math[k]) for k in full.math),
        "direct_and_reviewed_overlap": [k for k in full.math if direct_math[k] and equivalent_math[k]],
        "missing_direct_capture": [k for k in full.math if not direct_math[k]],
    })
    report["coverage"]["source_assets"] = {
        "original_unique_files": len(source_assets),
        "accepted_unique_files": len(set(accepted_assets) & source_assets),
        "missing_accepted_files": sorted(source_assets - set(accepted_assets)),
    }
    report["unregistered_drafts_not_counted"] = sorted(
        path.name for path in (root / "translation").glob("A30-U*.vi.md")
        if path.name not in {c["slug"] + ".vi.md" for c in configs.values()})
    for path, before in snapshots.items():
        try:
            if digest(path.read_bytes()) != before:
                changed_reads.add(path)
        except OSError:
            changed_reads.add(path)
    for path in sorted(changed_reads):
        issue("snapshot_changed_during_audit", str(path))
    report["input_sha256"] = {str(path): value for path, value in sorted(snapshots.items())}
    report["snapshot_stable"] = not any(x["code"] == "snapshot_changed_during_audit"
                                         for x in report["issues"])
    missing = any(row["missing_from_accepted_readers"]
                  for row in report["coverage"].values() if "missing_from_accepted_readers" in row)
    missing = missing or bool(report["coverage"]["source_assets"]["missing_accepted_files"])
    report["result"] = ("integrity_errors" if report["issues"] else
                        "incomplete_or_unverified" if missing else "structural_checks_pass")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="language package directory")
    parser.add_argument("--source", type=Path, default=SOURCE, help="existing pinned full EN module")
    args = parser.parse_args()
    result = audit(args.root, args.source)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "structural_checks_pass" else 1


if __name__ == "__main__":
    sys.exit(main())
