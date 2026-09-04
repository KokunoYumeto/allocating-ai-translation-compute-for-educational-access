"""Read-only structural coverage audit of the pinned m49304 pedagogical scope.

Print JSON; write no files, run no builders/checkers and fetch nothing. Registered
excerpts are not accepted readers unless current canon/build/visual receipts bind
their actual bytes. Missing direct MathML capture is NOT automatically semantic
loss: exact XML and nearby draft context are reported for individual review.
This separate m49304 implementation deliberately does not change the m49301
auditor. Module claims are checked against actual excerpt contents: source IDs
can collide across modules. XML comments remain archival, never active answers.
This tool does not approve rendered equivalents or prove translation meaning,
mathematical truth, native fluency, or completion of a module/book/assignment.

Optional provenance/m49304-rendered-equivalents.json schema:
{"schema":1,"module":"m49304","source_module_sha256":"...",
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
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from build import (Inspector, prune_empty_math_layout, validate_math_markup,
                   validate_reader_links)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml"
SOURCE_SHA = "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"
MODULE = "m49304"
CN = "http://cnx.rice.edu/cnxml"
MD = "http://cnx.rice.edu/mdml"
MATH = "http://www.w3.org/1998/Math/MathML"
EXERCISES_ID = "fs-id1165135176628"
PLACEHOLDER = re.compile(r"\{\{math:([^:}]+):(\d+)\}\}")
ANCHOR = re.compile(r"\{#([^\s}]+)(?:\s+[^}]*)?\}")
GENERIC_ID = re.compile(r"(?:para|list|term)-\d+\Z")
COMMENT = re.compile(rb"<!--(.*?)-->", re.S)


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


def canonical_source_math(node):
    """Source mtext is exact, including NBSP; only XML indentation is ignored."""
    return (node.tag, tuple(sorted(node.attrib.items())),
            node.text if local(node.tag) == "mtext" else (node.text or "").strip(),
            tuple((canonical_source_math(child), (child.tail or "").strip())
                  for child in node))


def protected_mtext(text):
    """Localization may change words, not embedded numbers/operators/currency."""
    return re.findall(r"[0-9]+(?:[.,][0-9]+)*|[+\-−=<>≤≥≠∞{}\[\]();|*/×÷^$]", text)


def validate_rendered_math_namespaces(node):
    """Local-name equality cannot turn a foreign XML element into MathML.

    Accept the two serializations used by the reader checks: uniformly bare
    MathML tags, or uniformly MathML-namespaced tags. Do not accept foreign or
    mixed-namespace children merely because they are also named mi/mn/mrow.
    """
    namespace = node.tag[1:].split("}", 1)[0] if node.tag.startswith("{") else ""
    if namespace not in ("", MATH):
        raise ValueError(f"foreign rendered math root namespace: {namespace}")
    for child in node.iter():
        child_namespace = child.tag[1:].split("}", 1)[0] if child.tag.startswith("{") else ""
        if child_namespace != namespace:
            raise ValueError(f"foreign or mixed rendered MathML namespace: {child.tag}")


class ReferenceInspector(HTMLParser):
    """Keep prose-link occurrences distinct from generated navigation links."""
    def __init__(self):
        super().__init__()
        self.navigation_depth = 0
        self.body_links, self.navigation_links = [], []

    def handle_starttag(self, tag, attrs):
        if tag == "nav":
            self.navigation_depth += 1
        if tag == "a":
            destination = self.navigation_links if self.navigation_depth else self.body_links
            destination.append(dict(attrs).get("href", ""))

    def handle_endtag(self, tag):
        if tag == "nav":
            self.navigation_depth = max(0, self.navigation_depth - 1)


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


def module_evidence(config, document, inventory, full):
    """Claims route an excerpt; matching source atoms/math validate it later.

    A generic term/paragraph ID alone is never evidence of module membership.
    A non-generic matching ID AND tag detects content hidden behind a foreign
    filename, including a wholly mislabeled registered unit. Explicit claims
    are evidence, not authorization to skip comparison with the actual source.
    """
    claims = {}
    declared = config.get("source_module")
    if declared is not None:
        if not isinstance(declared, str) or not re.fullmatch(r"m\d+", declared):
            raise ValueError("invalid registry source_module declaration")
        claims["registry.source_module"] = declared
    match = re.match(r"(m\d+)(?=[.-])", Path(config.get("source", "")).name)
    if match:
        claims["source_filename"] = match[1]
    content_id = document.find(f".//{{{MD}}}content-id")
    if content_id is not None and normalized(content_id.text):
        claims["excerpt.metadata.content-id"] = normalized(content_id.text)
    strong = [identity for identity, node in inventory.ids.items()
              if not GENERIC_ID.fullmatch(identity) and identity in full.ids
              and node.tag == full.ids[identity].tag]
    values = set(claims.values())
    conflict = len(values) > 1 or bool(values and MODULE not in values and strong)
    selected = MODULE in values or bool(strong)
    return {"claims": claims, "matching_nongeneric_id_and_tag": strong,
            "selected": selected, "conflict": conflict,
            "reason": ("contradictory_module_evidence" if conflict else
                       "target_claim_and_or_actual_content" if selected else
                       "explicit_other_module" if values else "ambiguous_or_other_content")}


def comment_inventory(data):
    """Inventory archival XML without activating it; raw and LF hashes differ.

    The normal active Inventory uses ElementTree's default comment exclusion.
    A second parser supplies each comment's nearest active source-ID owner.
    The raw payload retains exact CRLF/LF evidence; the explicitly named LF
    digest permits the already documented extraction line-ending conversion.
    """
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    document = ET.fromstring(data, parser=parser)
    located = []

    def walk(node, owner=None):
        owner = node.get("id", owner)
        for child in node:
            if child.tag is ET.Comment:
                located.append((owner, child.text or ""))
            else:
                walk(child, owner)
    walk(document)
    raw = COMMENT.findall(data)
    if len(raw) != len(located):
        raise ValueError("raw/comment-parser inventories differ")
    counts = Counter()
    records = []
    for payload, (owner, parsed) in zip(raw, located):
        counts[owner] += 1
        normalized_payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        record = {
            "key": f"{owner or 'document'}:comment:{counts[owner]}",
            "owner_source_id": owner, "raw_payload_sha256": digest(payload),
            "lf_payload_sha256": digest(normalized_payload),
            "raw_crlf_count": payload.count(b"\r\n"),
            "payload_xml": normalized_payload.decode("utf-8"),
            "inactive_ids": [], "inactive_math_keys": [],
            "active_coverage_contribution": 0,
        }
        try:
            wrapper = ET.fromstring(
                f'<archive xmlns="{CN}" xmlns:m="{MATH}">{parsed}</archive>')
            archived = Inventory([wrapper])
            record["inactive_ids"] = list(archived.ids)
            record["inactive_math_keys"] = list(archived.math)
            record["interpretation"] = "inactive_xml_fragment_not_a_source_answer"
        except (ET.ParseError, ValueError):
            record["interpretation"] = "uninterpreted_archival_comment_not_active_content"
        records.append(record)
    return records


def audit(root=ROOT, source=SOURCE, expected_source_sha=SOURCE_SHA):
    root, source = Path(root).resolve(), Path(source).resolve()
    snapshots = {}
    changed_reads = set()
    report = {
        "schema": 1, "module": "m49304", "mode": "read_only_no_network_no_build",
        "result": "incomplete_or_unverified", "issues": [], "units": {},
        "module_routing": {},
        "limits": [
            "Structural coverage is not proof of translation semantics, mathematical correctness or native fluency.",
            "Direct source MathML, source-excerpt retention and accepted reader coverage are distinct measures.",
            "Manual mathematical restatements are not approved or rejected semantically by this audit.",
            "Only registered units with current accepted canon/build/visual receipts count as accepted readers.",
            "Content atoms verify source-excerpt retention, not a sentence-by-sentence semantic alignment of translated prose.",
            "XML comments contribute no active IDs, MathML, exercises or source answers; their archival retention is reported separately.",
            "External links are syntax/retention checked but never fetched or asserted to remain available.",
            "Recorded visual acceptance is hash-bound; this tool does not inspect pixels or rerun native-language review.",
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

    def issue(code, detail, unit=None, *, severity="integrity_error"):
        entry = {"code": code, "detail": detail, "severity": severity}
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
        content_id = document.find(f".//{{{MD}}}content-id")
        if content_id is not None and normalized(content_id.text) != MODULE:
            raise ValueError("pinned full source declares a different module")
        full = Inventory(pedagogical_roots(document))
        source_comments = comment_inventory(source_data)
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
    admitted_evidence = defaultdict(list)
    for path in sorted((root / "provenance").glob("*asset-notice*.json")):
        try:
            notice = load(path)
            # Existing root notices use either the original flat ledger-row
            # list or {module, unit, assets:[{filename, rights,...}]} (the
            # U022 notice calls that nested row inherited_rights).
            # Author draft provenance is deliberately not an admission source.
            if isinstance(notice, list):
                entries = notice
            elif isinstance(notice, dict) and isinstance(notice.get("assets"), list):
                entries = notice["assets"]
            else:
                raise ValueError("unsupported existing asset-notice schema")
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValueError("asset-notice entries must be objects")
                row = entry.get("rights", entry.get("inherited_rights", entry))
                if not isinstance(row, dict):
                    raise ValueError("inherited asset-notice rights must be an object")
                if row.get("admission") != "admitted" or not row.get("sha256"):
                    continue
                name = Path(row["asset_path"]).name
                if "rights" in entry or "inherited_rights" in entry:
                    if entry.get("filename") != name:
                        raise ValueError(f"notice filename/rights path mismatch: {name}")
                    for field in ("sha256", "actual_sha256"):
                        if field in entry and entry[field] != row["sha256"]:
                            raise ValueError(f"notice {field}/rights hash mismatch: {name}")
                admitted[name].add(row["sha256"])
                admitted_evidence[name].append({
                    "notice": str(path.relative_to(root)), "sha256": row["sha256"],
                    "rights_component_id": row.get("rights_component_id"),
                    "license_id": row.get("license_id"),
                })
        except (OSError, ValueError, KeyError, TypeError) as error:
            issue("asset_notice_error", f"{path.name}: {error}")

    excerpt_owners, accepted_owners = defaultdict(set), defaultdict(set)
    excerpt_atoms, accepted_atoms = defaultdict(set), defaultdict(set)
    excerpt_math, direct_math, equivalent_math = defaultdict(set), defaultdict(set), defaultdict(set)
    excerpt_comments, accepted_comments = defaultdict(set), defaultdict(set)
    ledger_entries = defaultdict(list)
    ledger_path = root / "provenance/m49304-rendered-equivalents.json"
    report["equivalence_ledger"] = {
        "path": str(ledger_path), "present": ledger_path.is_file(),
        "basis": "Recorded reviewer judgment plus verified exact source/draft/reader bindings; not automated semantic proof.",
    }
    if ledger_path.is_file():
        try:
            ledger = load(ledger_path)
            if (not isinstance(ledger, dict) or ledger.get("schema") != 1 or ledger.get("module") != "m49304"
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
    source_images = {key: atom for key, atom in full.atoms.items()
                     if atom.get("tag") == f"{{{CN}}}image"}
    source_assets = {Path(atom["attributes"]["src"]).name for atom in source_images.values()}
    source_url_atoms = {key: atom for key, atom in full.atoms.items()
                        if atom.get("tag") == f"{{{CN}}}link"
                        and atom["attributes"].get("url")}
    source_reference_atoms = {key: atom for key, atom in full.atoms.items()
                              if atom.get("tag") == f"{{{CN}}}link"
                              and (atom["attributes"].get("target-id") or atom["attributes"].get("document"))}
    accepted_image_occurrences, accepted_url_atoms = defaultdict(set), defaultdict(set)
    accepted_reference_atoms = defaultdict(set)
    accepted_assets = defaultdict(set)
    reference_source_cache = {}

    def reference_source_identity(target_unit):
        """Resolve a link's source module/IDs from the actual registered excerpt."""
        if target_unit not in reference_source_cache:
            target_config = configs[target_unit]
            target_path = relative_file(root, target_config["source"])
            target_data = read(target_path)
            target_document = ET.fromstring(target_data)
            target_inventory = Inventory([target_document])
            evidence = module_evidence(target_config, target_document, target_inventory, full)
            if evidence["conflict"]:
                raise ValueError(f"conflicting target module evidence: {target_unit}")
            values = set(evidence["claims"].values())
            target_module = next(iter(values)) if values else MODULE if evidence["selected"] else None
            if target_module is None:
                raise ValueError(f"unresolved target source module: {target_unit}")
            reference_source_cache[target_unit] = {
                "module": target_module, "source_ids": set(target_inventory.ids),
                "source_excerpt_sha256": digest(target_data),
            }
        return reference_source_cache[target_unit]

    for unit, config in configs.items():
        if not unit.startswith("A30-"):
            continue
        start_issues = len(report["issues"])
        unit_report = {"accepted_receipts": False, "direct_math_capture_gaps": [],
                       "verified_reviewed_equivalent_keys": [],
                       "technical_anchor_aliases": [], "source_content_mismatches": [],
                       "source_math_mismatches": [], "mtext_localizations": [],
                       "archival_comments": []}
        try:
            if not isinstance(config, dict):
                raise ValueError("unit registry entry must be an object")
            source_path = relative_file(root, config["source"])
            excerpt_data = read(source_path)
            excerpt_document = ET.fromstring(excerpt_data)
            excerpt = Inventory([excerpt_document])
            evidence = module_evidence(config, excerpt_document, excerpt, full)
            report["module_routing"][unit] = evidence
            if evidence["conflict"]:
                issue("excerpt_module_conflict", evidence, unit)
                continue
            if not evidence["selected"]:
                continue
            report["units"][unit] = unit_report
            math_text = config.get("math_text", {})
            if (not isinstance(math_text, dict) or
                    not all(isinstance(old, str) and old and isinstance(new, str)
                            for old, new in math_text.items())):
                raise ValueError("math_text must be an object with nonempty string keys and string values")
            if "prune_empty_math_layout" in config and type(config["prune_empty_math_layout"]) is not bool:
                raise ValueError("prune_empty_math_layout must be a JSON boolean")
            minimum_canon_examples = config.get("minimum_canon_examples", 1)
            if type(minimum_canon_examples) is not int or minimum_canon_examples < 1:
                raise ValueError("minimum_canon_examples must be a positive JSON integer")
            if type(config.get("images")) is not int or config["images"] < 0:
                raise ValueError("images must be a nonnegative JSON integer")
            draft_path = relative_file(root, f"translation/{config['slug']}.vi.md")
            reader_path = relative_file(root, f"review/{config['slug']}.vi.html")
            draft_data = read(draft_path)
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
            archival = comment_inventory(excerpt_data)
            unit_report["archival_comments"] = archival
            archived_ids = {identity for row in source_comments for identity in row["inactive_ids"]}
            activated = sorted(archived_ids & set(excerpt.ids))
            if activated:
                issue("inactive_source_content_activated", activated, unit)
            matched_comment_keys = []
            for original in source_comments:
                if original["owner_source_id"] not in excerpt.ids:
                    continue
                matches = [row for row in archival if row["key"] == original["key"]
                           and row["lf_payload_sha256"] == original["lf_payload_sha256"]]
                if len(matches) != 1:
                    issue("archival_comment_missing_or_changed", original["key"], unit)
                else:
                    matched_comment_keys.append(original["key"])
                    excerpt_comments[original["key"]].add(unit)
            for row in archival:
                if not any(row["key"] == original["key"]
                           and row["lf_payload_sha256"] == original["lf_payload_sha256"]
                           for original in source_comments):
                    issue("unrecognized_archival_comment", row["key"], unit)
            if any(count != 1 for count in anchors.values()):
                issue("duplicate_draft_anchor", [k for k, n in anchors.items() if n != 1], unit)
            for identity, node in excerpt.ids.items():
                if identity not in full.ids:
                    issue("unknown_excerpt_id", identity, unit)
                elif node.tag != full.ids[identity].tag:
                    issue("source_tag_mismatch", identity, unit)
                else:
                    excerpt_owners[identity].add(unit)
                    actual_parent = excerpt.parents.get(node)
                    while actual_parent is not None and not actual_parent.get("id"):
                        actual_parent = excerpt.parents.get(actual_parent)
                    expected_parent = full.parents.get(full.ids[identity])
                    while expected_parent is not None and expected_parent.get("id") not in excerpt.ids:
                        expected_parent = full.parents.get(expected_parent)
                    actual_id = actual_parent.get("id") if actual_parent is not None else None
                    expected_id = expected_parent.get("id") if expected_parent is not None else None
                    if actual_id != expected_id:
                        issue("source_excerpt_parentage_mismatch",
                              {"source_id": identity, "expected_nearest_retained_parent": expected_id,
                               "actual_nearest_retained_parent": actual_id}, unit)
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
                if key in full.math and canonical_source_math(math) == canonical_source_math(full.math[key]):
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
            try:
                validate_math_markup(reader)
            except AssertionError as error:
                issue("reader_math_markup_invalid", str(error), unit)
            for kind, receipt in (("canon", canon), ("build", build), ("visual", visual)):
                if not isinstance(receipt, dict):
                    raise ValueError(f"{kind} receipt must be an object")
                if receipt.get("unit") != unit:
                    issue("receipt_unit_mismatch", kind, unit)
            wrong_flags = [field for field in ("draft_checked", "final_checked")
                           if field in canon and type(canon[field]) is not bool]
            if wrong_flags:
                issue("canon_acceptance_flag_type_error", wrong_flags, unit)
            if canon.get("draft_checked") is not True or canon.get("final_checked") is not True:
                issue("canon_not_accepted", "draft_checked/final_checked", unit, severity="unverified")
            consulted = canon.get("examples_consulted", [])
            if (not isinstance(consulted, list) or
                    not all(isinstance(value, str) and value.strip() for value in consulted)):
                raise ValueError("canon examples_consulted must be a list of nonempty strings")
            if len(set(consulted)) < minimum_canon_examples:
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
                    issue("receipt_not_pass", kind, unit, severity="unverified")
                if receipt.get("html_sha256") != digest(reader_data):
                    issue("receipt_reader_hash_mismatch", kind, unit)
            if build.get("canon_review") != f"canon/review-{unit}.json":
                issue("build_canon_path_mismatch", build.get("canon_review"), unit)
            if build.get("visual_review") != config["visual_receipt"]:
                issue("build_visual_path_mismatch", build.get("visual_review"), unit)
            for field, actual in (("html_bytes", len(reader_data)),
                                  ("html_ids", len(inspector.ids)),
                                  ("mathml_expressions", inspector.math),
                                  ("source_math_rendered_count", len(inspector.source_math)),
                                  ("preserved_source_ids", len(excerpt.ids)),
                                  ("embedded_images", len(inspector.images))):
                if field in build and (type(build[field]) is not int or build[field] != actual):
                    issue("build_observed_count_mismatch",
                          {"field": field, "recorded": build[field], "actual": actual}, unit)
            if "required_ids" in config and Counter(config["required_ids"]) != Counter(excerpt.ids.keys()):
                issue("registry_excerpt_id_inventory_mismatch", "required_ids differ from actual excerpt", unit)
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
                try:
                    validate_rendered_math_namespaces(node)
                except ValueError as error:
                    issue("reader_math_namespace_invalid",
                          {"reference": node.get("data-source"), "error": str(error)}, unit)
            for reference, math in zip(placeholder_refs, inserted_nodes):
                expected = deepcopy(math)
                for element in expected.iter():
                    element.tag = local(element.tag)
                    if local(element.tag) == "mtext" and element.text:
                        before = element.text
                        for old, new in math_text.items():
                            element.text = element.text.replace(old, new)
                        if element.text != before:
                            unit_report["mtext_localizations"].append({
                                "reference": reference, "source_text": before,
                                "localized_text": element.text,
                                "basis": "Exact registered substitutions, not automated linguistic approval.",
                            })
                        if protected_mtext(before) != protected_mtext(element.text):
                            issue("mtext_numeric_or_operator_payload_changed",
                                  {"reference": reference, "before": before, "after": element.text}, unit)
                if config.get("prune_empty_math_layout"):
                    root_arities = [len(node) for node in expected.iter() if local(node.tag) == "mroot"]
                    prune_empty_math_layout(expected)
                    if root_arities != [len(node) for node in expected.iter() if local(node.tag) == "mroot"]:
                        issue("source_root_arity_changed_by_pruning", reference, unit)
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
            if links["external_links"] != build.get("external_links", []):
                issue("external_link_receipt_mismatch", "current external href inventory differs", unit)
            for field, actual in (("internal_links", links["local_anchor_links"]),
                                  ("cross_reader_link_count", len(links["cross_reader_links"])),
                                  ("external_link_count", len(links["external_links"]))):
                if field in build and (type(build[field]) is not int or build[field] != actual):
                    issue("build_link_count_mismatch", {"field": field, "actual": actual}, unit)
            body = ReferenceInspector()
            body.feed(reader)
            unit_report["navigation_links_not_source_references"] = len(body.navigation_links)
            excerpt_reference_atoms = {key: atom for key, atom in excerpt.atoms.items()
                                       if atom.get("tag") == f"{{{CN}}}link"
                                       and (atom["attributes"].get("target-id") or atom["attributes"].get("document"))}
            unit_report["source_reference_retention"] = []
            unit_report["reference_resolution_notes"] = []
            candidates = []
            cross_by_href = {row["href"]: row for row in links["cross_reader_links"]}
            if excerpt_reference_atoms:
                for index, href in enumerate(body.body_links):
                    parsed = urlsplit(href)
                    if parsed.scheme or parsed.netloc or not parsed.fragment:
                        continue
                    anchor = unquote(parsed.fragment, encoding="utf-8", errors="strict")
                    if not parsed.path:
                        identity = {"module": MODULE, "source_ids": set(excerpt.ids),
                                    "source_excerpt_sha256": digest(excerpt_data)}
                        target_unit, target_sha = unit, digest(reader_data)
                    else:
                        cross = cross_by_href[href]
                        target_unit, target_sha = cross["target_unit"], cross["target_sha256"]
                        try:
                            identity = reference_source_identity(target_unit)
                        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
                            # An unrelated supplementary target need not have
                            # source provenance, but cannot satisfy a source reference.
                            unit_report["reference_resolution_notes"].append({"href": href, "error": str(error)})
                            continue
                    candidates.append({
                        "reader_body_link_index": index, "href": href,
                        "target_unit": target_unit, "target_module": identity["module"],
                        "target_anchor": anchor, "target_is_source_id": anchor in identity["source_ids"],
                        "target_source_excerpt_sha256": identity["source_excerpt_sha256"],
                        "target_reader_sha256": target_sha,
                    })
            used_reference_links = set()
            # Bind specific anchors first; a document-only reference may then
            # use any remaining link into that source module, including a VI guide anchor.
            for key, atom in sorted(excerpt_reference_atoms.items(),
                                    key=lambda item: not bool(item[1]["attributes"].get("target-id"))):
                attributes = atom["attributes"]
                target_module = attributes.get("document", MODULE)
                target_id = attributes.get("target-id")
                matching = [row for row in candidates
                            if row["reader_body_link_index"] not in used_reference_links
                            and row["target_module"] == target_module
                            and (not target_id or (row["target_anchor"] == target_id and row["target_is_source_id"]))]
                match = matching[0] if matching else None
                record = {"source_atom": key, "source_target_module": target_module,
                          "source_target_id": target_id, "retained": match is not None,
                          "resolution": "exact_module_and_source_anchor" if target_id else "source_module_only"}
                if match:
                    used_reference_links.add(match["reader_body_link_index"])
                    record["reader_reference"] = match
                else:
                    issue("source_target_reference_not_rendered", record, unit)
                unit_report["source_reference_retention"].append(record)
            excerpt_url_atoms = {key: atom for key, atom in excerpt.atoms.items()
                                 if atom.get("tag") == f"{{{CN}}}link"
                                 and atom["attributes"].get("url")}
            unit_report["source_external_url_retention"] = []
            available_urls = Counter(body.body_links)
            for key, atom in excerpt_url_atoms.items():
                href = atom["attributes"]["url"]
                retained = available_urls[href] > 0
                if retained:
                    available_urls[href] -= 1
                unit_report["source_external_url_retention"].append({
                    "source_atom": key, "href": href, "rendered_link_present": retained,
                    "verification": "unverified", "fetched": False,
                })
                if not retained:
                    issue("source_external_url_not_rendered", {"key": key, "href": href}, unit)

            embedded = []
            for image in inspector.images:
                src = image.get("src", "")
                if not image.get("alt") or not re.match(r"data:image/[^;,]+;base64,", src):
                    issue("reader_image_not_embedded_or_described", src[:80], unit)
                else:
                    embedded.append(digest(base64.b64decode(src.split(",", 1)[1], validate=True)))
            unit_assets = set()
            image_atoms = {key: atom for key, atom in excerpt.atoms.items()
                           if atom.get("tag") == f"{{{CN}}}image"}
            required_embedded = Counter()
            for key, image in image_atoms.items():
                name = Path(image["attributes"]["src"]).name
                asset = read(relative_file(root, "assets/" + name))
                asset_sha = digest(asset)
                required_embedded[asset_sha] += 1
                if asset_sha not in admitted[name]:
                    issue("source_asset_admitted_hash_missing", name, unit)
                if asset_sha not in embedded:
                    issue("source_asset_not_rendered", name, unit)
                unit_assets.add(name)
            for asset_sha, required in required_embedded.items():
                if Counter(embedded)[asset_sha] < required:
                    issue("source_image_occurrence_not_rendered",
                          {"sha256": asset_sha, "required": required,
                           "rendered": Counter(embedded)[asset_sha]}, unit)
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
            unit_report["source_asset_notice_evidence"] = {
                name: admitted_evidence[name] for name in sorted(unit_assets)}
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
                for key in image_atoms:
                    if unit in excerpt_atoms[key]:
                        accepted_image_occurrences[key].add(unit)
                for key in excerpt_url_atoms:
                    if unit in excerpt_atoms[key]:
                        accepted_url_atoms[key].add(unit)
                for key in excerpt_reference_atoms:
                    if unit in excerpt_atoms[key]:
                        accepted_reference_atoms[key].add(unit)
                for key in matched_comment_keys:
                    accepted_comments[key].add(unit)
        except (OSError, ValueError, KeyError, IndexError, TypeError, ET.ParseError, AssertionError) as error:
            report["units"].setdefault(unit, unit_report)
            issue("unit_input_or_integrity_error", str(error), unit,
                  severity="unverified" if isinstance(error, FileNotFoundError) else "integrity_error")
        unit_report["issue_count"] = len(report["issues"]) - start_issues

    for unit, entries in ledger_entries.items():
        if entries and unit not in report["units"]:
            issue("equivalent_review_unit_outside_module", unit)

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
                                 if local(node.tag) == "definition" and
                                 any(local(a.tag) == "glossary" for a in ancestors(node))],
        "active_source_solutions": [identity for identity, node in full.ids.items()
                                    if local(node.tag) == "solution"],
        "teaching_sections": [identity for identity, node in full.ids.items()
                              if local(node.tag) == "section" and identity != EXERCISES_ID
                              and not any(a.get("id") == EXERCISES_ID for a in ancestors(node))],
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
    report["counts"]["end_exercises"]["original_sequence"] = [
        {"number": index, "source_id": identity,
         "active_source_solution_ids": [n.get("id") for n in full.ids[identity].iter(f"{{{CN}}}solution")],
         "accepted_units": sorted(accepted_owners[identity])}
        for index, identity in enumerate(groups["end_exercises"], 1)]
    abstract = document.find(f".//{{{MD}}}abstract")
    objective_nodes = list(abstract.iter(f"{{{CN}}}item"))
    objective_keys = [full.nodekeys[node] for node in objective_nodes]
    covered_objectives = {
        key: all(accepted_atoms[atom_key] for atom_key in full.atoms
                 if atom_key == key or atom_key.startswith(key + "/"))
        for key in objective_keys}
    report["counts"]["learning_objectives"] = {
        "original": len(objective_nodes),
        "accepted": sum(covered_objectives.values()),
        "missing": [full.atoms[k]["text"] for k in objective_keys if not covered_objectives[k]],
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
    report["missing_direct_math_evidence"] = [
        {"source_math_key": key,
         "source_mathml": source_math_bytes(full.math[key]).decode("utf-8"),
         "source_math_sha256": digest(source_math_bytes(full.math[key])),
         "source_text": normalized("".join(full.math[key].itertext())),
         "registered_excerpt_units": sorted(excerpt_math[key]),
         "reviewed_equivalent_units": sorted(equivalent_math[key]),
         "draft_context_location": "units.<unit>.direct_math_capture_gaps, when the registered draft omits a capture",
         "meaning": "Missing accepted direct capture is not an automatic judgment of semantic omission."}
        for key in full.math if not direct_math[key]]
    report["coverage"]["source_assets"] = {
        "original_unique_files": len(source_assets),
        "accepted_unique_files": len(set(accepted_assets) & source_assets),
        "missing_accepted_files": sorted(source_assets - set(accepted_assets)),
        "original_image_occurrences": len(source_images),
        "accepted_image_occurrences": sum(bool(accepted_image_occurrences[k]) for k in source_images),
        "missing_accepted_image_atoms": [k for k in source_images if not accepted_image_occurrences[k]],
    }
    report["source_image_media_without_figure"] = [
        full.nodekeys[node] for node in full.nodekeys
        if node.tag == f"{{{CN}}}image"
        and not any(a.tag == f"{{{CN}}}figure" for a in ancestors(node))]
    report["coverage"]["source_external_urls"] = {
        "original_occurrences": len(source_url_atoms),
        "accepted_retained_occurrences": sum(bool(accepted_url_atoms[k]) for k in source_url_atoms),
        "missing_accepted_source_atoms": [k for k in source_url_atoms if not accepted_url_atoms[k]],
        "source_urls": [atom["attributes"]["url"] for atom in source_url_atoms.values()],
        "availability": "unverified_not_fetched",
    }
    report["coverage"]["source_references"] = {
        "original_occurrences": len(source_reference_atoms),
        "original_target_id_occurrences": sum(bool(atom["attributes"].get("target-id"))
                                               for atom in source_reference_atoms.values()),
        "original_document_only_occurrences": sum(not atom["attributes"].get("target-id")
                                                   for atom in source_reference_atoms.values()),
        "accepted_retained_occurrences": sum(bool(accepted_reference_atoms[k]) for k in source_reference_atoms),
        "missing_accepted_source_atoms": [k for k in source_reference_atoms if not accepted_reference_atoms[k]],
        "basis": "One distinct non-navigation reader href per source occurrence; exact actual target-excerpt module and source ID, or module only for a document-only source link. This is not semantic prose alignment.",
    }
    report["archival_comments"] = {
        "basis": "Inactive source comments are preserved as provenance, never activated or counted as pedagogical answers/math.",
        "comparison": "LF-normalized payload matching only; raw SHA and CRLF counts remain separate evidence, not a byte-identity waiver.",
        "source": source_comments,
        "inactive_ids": [identity for row in source_comments for identity in row["inactive_ids"]],
        "inactive_math_keys": [key for row in source_comments for key in row["inactive_math_keys"]],
        "registered_retention": {row["key"]: sorted(excerpt_comments[row["key"]]) for row in source_comments},
        "accepted_retention": {row["key"]: sorted(accepted_comments[row["key"]]) for row in source_comments},
        "missing_accepted_keys": [row["key"] for row in source_comments if not accepted_comments[row["key"]]],
        "active_coverage_contribution": 0,
    }
    report["unregistered_drafts_not_counted"] = sorted(
        path.name for path in (root / "translation").glob("A30-U*.vi.md")
        if path.name not in {c["slug"] + ".vi.md" for c in configs.values()
                             if isinstance(c, dict) and isinstance(c.get("slug"), str)})
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
    missing = missing or bool(report["coverage"]["source_assets"]["missing_accepted_image_atoms"])
    missing = missing or bool(report["coverage"]["source_external_urls"]["missing_accepted_source_atoms"])
    missing = missing or bool(report["coverage"]["source_references"]["missing_accepted_source_atoms"])
    missing = missing or bool(report["archival_comments"]["missing_accepted_keys"])
    report["integrity_error_count"] = sum(row["severity"] == "integrity_error" for row in report["issues"])
    report["unverified_issue_count"] = sum(row["severity"] == "unverified" for row in report["issues"])
    report["result"] = ("integrity_errors" if report["integrity_error_count"] else
                        "incomplete_or_unverified" if missing or report["issues"] else "structural_checks_pass")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="language package directory")
    parser.add_argument("--source", type=Path, default=SOURCE, help="existing pinned full EN module")
    args = parser.parse_args()
    result = audit(args.root, args.source)
    # Windows redirected stdout can default to cp1252, which cannot encode
    # Vietnamese diagnostic/source context. Keep the JSON CLI UTF-8 even when
    # the caller did not supply Python -X utf8 or PYTHONIOENCODING.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "structural_checks_pass" else 1


if __name__ == "__main__":
    sys.exit(main())
