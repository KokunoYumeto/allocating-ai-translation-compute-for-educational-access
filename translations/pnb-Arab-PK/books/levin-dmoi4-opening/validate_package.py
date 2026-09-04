#!/usr/bin/env python3
"""Validate this bounded package offline without rebuilding or changing content.

Run from any directory: python path/to/validate_package.py
Requires Python 3.10+, lxml and Pillow, as does build.py. The sole write target
is qa/PACKAGE_VALIDATION.json. Support/canon assemblers are replayed in memory;
their writes are intercepted. A process/network/write audit hook fails closed.
No external citation availability or independent linguistic quality is certified.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
RECEIPT = BASE / "qa/PACKAGE_VALIDATION.json"
UNITS = ("b10-frontmatter", "b10-unit-001", "b10-unit-002")
FINDINGS = []
CHECKS = 0
from lxml import etree as E, html as LH


def audit(event, args):
    if event in {"subprocess.Popen", "os.system", "socket.connect", "socket.getaddrinfo"}:
        raise RuntimeError("External operation forbidden during package validation")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name, mode, flags = args[:3]
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            if Path(os.fsdecode(name)).resolve() != RECEIPT.resolve():
                raise RuntimeError("Validator attempted an unauthorized write")


sys.addaudithook(audit)


def check(condition, label):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            check(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text("utf-8"), object_pairs_hook=unique)


def ident(path):
    raw = path.read_bytes()
    return {"path": path.relative_to(BASE).as_posix(), "bytes": len(raw), "sha256": digest(raw)}


def relative(value):
    path = BASE / value
    check(path.resolve().is_relative_to(BASE.resolve()), "package-relative path escaped boundary")
    return path


def bind(row):
    path = relative(row["path"])
    check(path.is_file(), "required file missing: " + row["path"])
    check(ident(path) == {k: row[k] for k in ("path", "bytes", "sha256")}, "current identity differs: " + row["path"])


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def intake_qa():
    intake = read_json(BASE / "INTAKE_MANIFEST.json")
    rows = intake["files"]
    check(intake["result"] == "pass" and intake["file_count"] == len(rows) == 53, "exact 53-file intake")
    check(len({r["path"] for r in rows}) == 53, "unique intake paths")
    for row in rows:
        check(row["path"].startswith("frozen/"), "intake path outside frozen authority")
        bind(row)
    check(sum(r["bytes"] for r in rows) == intake["total_bytes"], "intake total bytes")
    return {"result": "pass", "files": 53, "bytes": intake["total_bytes"], "manifest": ident(BASE / "INTAKE_MANIFEST.json")}


def source_qa():
    replay = read_json(BASE / "qa/OFFLINE_REPLAY.json")
    check(replay["result"] == "pass" and replay["replay_count"] == 2, "sealed successful source replay")
    bind(replay["build_script"])
    bind(replay["intake"])
    check(replay["replays"][0] == replay["replays"][1], "recorded replay identities agree")
    for row in replay["replays"][0] + replay["exact_dependency_aliases"]:
        bind(row)
    proof = read_json(BASE / "qa/OFFLINE_REPLAY_REPRODUCIBILITY.json")
    check(proof["result"] == "pass", "independent source replay passed")
    bind(proof["build_script"])
    bind(proof["verified_receipt"])
    build = module("recovered_package_build", "build.py")
    build.verify_intake()
    build.retained_notice_policy()
    prepares = build.install_adapters()
    results = []
    for unit, prep, expected_keys, expected_nodes, suffix in zip(UNITS, prepares, (50, 157, 559), (101, 492, 1602), ("frontmatter", "001", "002")):
        path = BASE / ("reader/" + unit + ".html")
        check(path.read_bytes() == (BASE / ("frozen/reader/" + unit + ".html")).read_bytes(), unit + " exact reader comparator")
        args = prep.load_inputs()
        m, t = args[:2]
        document = LH.fromstring(path.read_text("utf-8"))
        seen = document.xpath('//*[@data-source-node]')
        if suffix == "frontmatter":
            helper = importlib.import_module("qa_b10_frontmatter")
            original = dict(helper.expected_source(args[3]))
            keys = m["source_keys"]
            notice = prep.notice_record(m, args[4])
        elif suffix == "001":
            original = {prep.key(n): n for n in args[2].iter()}
            keys = m["expected_source_keys"]
            notice = prep.notice_record(m, args[3])
        else:
            original = args[4]
            keys = m["expected_source_keys"]
            notice = prep.notice_record(m)
        check(notice == read_json(prep.NOTICES), unit + " exact source/math/component notice")
        check([n.get("data-source-key") for n in document.xpath('//*[@data-source-key]')] == keys == list(t["source_blocks"]), unit + " complete ordered translation keys")
        check(len(keys) == expected_keys and len(seen) == expected_nodes, unit + " bounded source counts")
        check(len({n.get("data-source-node") for n in seen}) == expected_nodes and set(original) == {n.get("data-source-node") for n in seen}, unit + " exact original node closure")
        xml_ids = 0
        for rendered in seen:
            node = original[rendered.get("data-source-node")]
            source_tag = "include" if suffix == "frontmatter" and node.tag == prep.XI else node.tag
            check(rendered.get("data-source-tag") == source_tag, unit + " source tag binding")
            check(json.loads(rendered.get("data-source-attributes")) == dict(node.attrib), unit + " original attribute binding")
            if node.get(prep.XID):
                xml_ids += 1
                check(rendered.get("id") == node.get(prep.XID), unit + " preserved XML ID")
            if node.tag in {"m", "me"}:
                check(rendered.get("data-source-tex") == node.text and rendered.get("data-source-tex-sha256") == digest(node.text.encode()), unit + " exact TeX owner/text/hash")
        tex = document.xpath('//*[@data-source-tex]')
        check(len(tex) == (0 if suffix == "frontmatter" else 105 if suffix == "001" else 337), unit + " mathematical scope")
        if suffix != "frontmatter":
            fixture = importlib.import_module("b10_" + suffix + "_math_expected")
            rows = notice["math_conversion"]["records"]
            for row in rows:
                check(row["tree"] == fixture.expected(row["source_tex"]), unit + " independent finite mathematical fixture")
        results.append({"unit": unit, "result": "pass", "source_keys": len(keys), "source_nodes": len(seen),
                        "source_xml_ids": xml_ids, "exact_tex_owners": len(tex), "reader": ident(path)})
    check(sum(r["source_keys"] for r in results) == 766, "766 total source keys")
    return {"result": "pass", "units": results, "total_source_keys": 766,
            "source_regeneration_repeated": False,
            "method": "Rechecked current source/translation/tree/ID/TeX/math-fixture/notice seals, aliases and exact reader bytes; verified existing two-run replay receipt instead of rebuilding unchanged source readers."}


def active_pages():
    return [BASE / "index.html"] + [p for folder in ("reader", "support", "canon") for p in sorted((BASE / folder).glob("*.html"))]


def page_qa():
    rows, broken = [], []
    for path in active_pages():
        raw = path.read_text("utf-8")
        root = LH.fromstring(raw)
        label = path.relative_to(BASE).as_posix()
        check(root.get("lang") == "pnb-Arab-PK" and root.get("dir") == "rtl", label + " locale and RTL")
        ids = root.xpath('//@id')
        check(len(ids) == len(set(ids)), label + " unique IDs")
        check(not root.xpath('//script|//iframe|//object|//embed'), label + " no executable runtime")
        check(not any(k.lower().startswith("on") for n in root.iter() for k in n.attrib), label + " no event handler")
        check(not re.search('[\ufffd\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069]', raw), label + " no replacement/Gurmukhi/directional override characters")
        math_nodes = root.xpath('//*[local-name()="math"] | //*[@data-source-tex] | //*[contains(concat(" ",normalize-space(@class)," ")," math ")]')
        for node in math_nodes:
            ancestry = [node] + list(node.iterancestors())
            direction = next((p.get("dir") for p in ancestry if p.get("dir")), None)
            check(direction == "ltr", label + " mathematical content explicitly LTR")
        local, external = 0, 0
        for node in root.xpath('//*[@href or @src]'):
            reference = node.get("href") if node.get("href") is not None else node.get("src")
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                check(url.scheme in {"http", "https", "mailto"}, label + " non-executable URL")
                check(node.tag not in {"script", "img", "iframe", "link"}, label + " no remote rendering resource")
                external += 1
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path.resolve()
            if not target.is_relative_to(BASE.resolve()) or not target.is_file():
                broken.append({"page": label, "reference": reference, "reason": "missing_or_outside_package"})
                continue
            if url.fragment and target.suffix.lower() == ".html":
                linked = root if target == path.resolve() else LH.fromstring(target.read_text("utf-8"))
                if unquote(url.fragment) not in linked.xpath('//@id'):
                    broken.append({"page": label, "reference": reference, "reason": "missing_fragment"})
            local += 1
        rows.append({"page": label, "local_references": local, "external_citations_not_fetched": external,
                     "ids": len(ids), "ltr_math_nodes": len(math_nodes)})
    for name in ("site.css", "frozen/styles/reader.css"):
        css = (BASE / name).read_text("utf-8")
        check(not re.search(r"@import|url\s*\(", css, re.I), name + " no unvalidated stylesheet dependencies")
    if broken:
        FINDINGS.extend({"stage": "active_pages", **f} for f in broken)
    return {"result": "fail" if broken else "pass", "pages": rows, "broken_references": broken,
            "limit": "Explicit RTL/LTR encodings and HTML parsing checked; this is not a visual glyph-layout or assistive-technology certificate."}


def literal(expression):
    value = ast.literal_eval(expression)
    check(isinstance(value, (set, tuple, list)), "bounded literal collection expected")
    return value


def support_qa():
    data = read_json(BASE / "support/practice.json")
    expected_ids = ["b10-support-set-01", "b10-support-function-02", "b10-support-sequence-03", "b10-support-graph-04", "b10-support-connective-05", "b10-support-quantifier-06"]
    check(data["locale"] == "pnb-Arab-PK" and data["origin"] == "newly_authored_support_not_Levin_source", "separate support origin/locale")
    check([i["id"] for i in data["items"]] == expected_ids, "six exact support exercise identities")
    items = data["items"]
    verified = []
    a, b = [literal(x) for x in re.findall(r'\{[^{}]+\}', items[0]["given"])]
    values = [literal(x) for x in re.findall(r'\{[^{}]+\}', items[0]["calculation"])]
    count = int(re.search(r'\|A ∪ B\| = (\d+)', items[0]["calculation"]).group(1))
    check(values == [a & b, a | b] and count == len(a | b), "support set intersection/union/cardinality")
    verified.append({"id": expected_ids[0], "computed": {"intersection": sorted(a & b), "union": sorted(a | b), "cardinality": len(a | b)}})
    relation = literal(items[1]["given"])
    domain, codomain = {0, 1, 2}, {0, 1, 4}
    images = defaultdict(set)
    for x, y in relation:
        images[x].add(y)
    check(set(images) == domain and all(len(images[x]) == 1 and images[x] <= codomain for x in domain), "support initial relation is total single-valued function")
    changed = relation | {(1, 4)}
    check({y for x, y in changed if x == 1} == {1, 4}, "support added pair violates single-valuedness")
    check(items[1]["calculation"] == "1 ↦ 1; 1 ↦ 4", "support function answer bindings")
    verified.append({"id": expected_ids[1], "computed": {"initial_function": True, "after_added_pair_function": False, "conflicting_outputs_for_1": [1, 4]}})
    check(items[2]["given"] == "a₀ = 1; aₙ₊₁ = aₙ + 3; aₙ = 1 + 3n", "support exact sequence initial condition/recurrence/domain index")
    sequence = [1]
    for _ in range(3):
        sequence.append(sequence[-1] + 3)
    displayed = [int(x) for x in re.findall(r'= (\d+)', items[2]["calculation"])]
    check(sequence == [1 + 3 * n for n in range(4)] == displayed, "support recurrence and closed-form arithmetic independently agree")
    verified.append({"id": expected_ids[2], "computed": {"indices": [0, 1, 2, 3], "values": sequence}, "limit": "Finite four-value check, not a proof for every index."})
    check(items[3]["given"] == "V = {A, B, C}; E = {{A, B}, {B, C}}", "support exact simple undirected graph")
    edges = {frozenset(("A", "B")), frozenset(("B", "C"))}
    degrees = {v: sum(v in edge for edge in edges) for v in "ABC"}
    displayed_degrees = {v: int(n) for v, n in re.findall(r'deg\(([ABC])\) = (\d+)', items[3]["calculation"])}
    check(degrees == displayed_degrees and frozenset(("A", "C")) not in edges and "{A, C} ∉ E" in items[3]["calculation"], "support graph degrees/nonedge/path distinction")
    verified.append({"id": expected_ids[3], "computed": {"degrees": degrees, "AC_edge": False, "A_to_C_path": ["A", "B", "C"]}})
    check(items[4]["given"] == "P ∧ Q; P ∨ Q; ¬P", "support connective formulas")
    p, q = True, False
    truth = [p and q, p or q, not p]
    check(re.findall(r': ([TF])', items[4]["calculation"]) == ["T" if v else "F" for v in truth], "support conjunction/inclusive-disjunction/negation truth values")
    verified.append({"id": expected_ids[4], "computed": {"P": p, "Q": q, "and_or_not": truth}})
    check(items[5]["given"] == "D = {0, 1, 2}; P(x) ⇔ 2 ∣ x", "support exact finite integer domain and evenness predicate")
    domain = {0, 1, 2}
    predicate = {x: x % 2 == 0 for x in domain}
    universal, existential = all(predicate.values()), any(predicate.values())
    negated = not universal
    counterexample_exists = any(not v for v in predicate.values())
    check(re.findall(r': ([TF])', items[5]["calculation"]) == ["T" if v else "F" for v in (universal, existential)], "support universal/existential truth values")
    check(negated == counterexample_exists and "¬∀x ∈ D P(x) ⇔ ∃x ∈ D ¬P(x)" in items[5]["calculation"], "support quantifier-negation domain law")
    verified.append({"id": expected_ids[5], "computed": {"domain": sorted(domain), "even_witnesses": [x for x in sorted(domain) if predicate[x]], "counterexamples": [x for x in sorted(domain) if not predicate[x]], "universal": universal, "existential": existential, "negation_equivalence": negated == counterexample_exists}})
    page = LH.fromstring((BASE / "support/practice.html").read_text("utf-8"))
    check(not page.xpath('//*[@data-source-node or @data-source-key]'), "new support is never source-attributed")
    check([n.get("id") for n in page.xpath('//*[@data-origin="newly-authored-support"]')] == expected_ids, "all six support articles independently marked")
    check(len(page.xpath('//article/details')) == 6, "six separately disclosed support answers")
    canon = LH.fromstring((BASE / "canon/terminology.html").read_text("utf-8"))
    check(not canon.xpath('//*[@data-source-node or @data-source-key]'), "new terminology register separate from source")
    coverage = read_json(BASE / "COVERAGE.json")
    check(coverage["total_source_slots"] == 766 and coverage["source_support_separation"] is True and coverage["new_support"]["exercise_count"] == coverage["new_support"]["answers_included"] == 6, "declared source/support coverage")
    for item in items:
        check(bool(item["answer"]) and bool(item["question"]) and item["source_topic"].startswith("../reader/"), "support question/answer/source-topic present")
    return {"result": "pass", "independent_answers": verified,
            "method": "Independent finite set/relation/recurrence/graph/Boolean/domain evaluation bound to the supplied givens and displayed symbolic answers.",
            "limit": "Punjabi explanations were inspected during production; exact assembler replay preserves them, but automated finite arithmetic is not a proof of natural-language translation quality."}


def assembler_qa():
    results = []
    for name, output in (("assemble_support.py", "support/practice.html"), ("assemble_canon.py", "canon/terminology.html")):
        assembler = module(name.removesuffix(".py"), name)
        captured = []
        def capture(path, raw):
            check(path.resolve() == (BASE / output).resolve(), "assembler write target is exact expected output")
            check(isinstance(raw, bytes), "assembler writes deterministic bytes")
            captured.append(raw)
            return len(raw)
        with patch.object(Path, "write_bytes", capture):
            first, second = assembler.build(), assembler.build()
        check(len(captured) == 2 and captured[0] == captured[1] == (BASE / output).read_bytes(), "support/canon in-memory source replay exact: " + output)
        check(first == second == ident(BASE / output), "assembler output identity agrees")
        results.append({"script": ident(BASE / name), "output": first, "result": "pass", "replays": 2, "writes_intercepted": True})
    return {"result": "pass", "assemblers": results}


def privacy_qa():
    intake = read_json(BASE / "INTAKE_MANIFEST.json")
    inherited = {r["path"]: r["sha256"] for r in intake["files"]}
    for row in intake["files"]:
        if row["path"].startswith(("frozen/assets/", "frozen/source-excerpts/", "frozen/provenance/", "frozen/reader/")):
            inherited[row["path"].removeprefix("frozen/")] = row["sha256"]
    patterns = {
        # A colon followed by an escaped set-opening brace is TeX function
        # notation, not a high-confidence filesystem path.
        "absolute_private_filesystem_path": re.compile(r'(?i)(?:\b[A-Z]:' + r'[\\/](?!\{)|/(?:home|Users)/[^\s/]+/|fi' + r'le:/{2,})'),
        "credential_token": re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{25,})\b'),
        "credential_assignment": re.compile(r'(?i)(?:api[_-]?key|access[_-]?token|authorization|password)\s*[:=]\s*["\x27]?(?:bearer\s+)?[A-Za-z0-9_./+-]{20,}'),
    }
    new_findings, inherited_findings, scanned = [], [], []
    excluded = {"qa/OFFLINE_REPLAY_PROGRESS.json", "qa/PACKAGE_VALIDATION.json"}
    for path in sorted(BASE.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(BASE).as_posix()
        if rel in excluded or "__pycache__" in path.parts or path.suffix.lower() in {".png", ".gif", ".jpg", ".jpeg", ".zip", ".pyc"}:
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            check(rel in inherited, "unclassified non-UTF-8 new public file: " + rel)
            continue
        exact_inherited = rel in inherited and digest(raw) == inherited[rel]
        if not exact_inherited:
            scanned.append(rel)
        for kind, pattern in patterns.items():
            for match in pattern.finditer(text):
                finding = {"path": rel, "line": text.count("\n", 0, match.start()) + 1, "kind": kind}
                (inherited_findings if exact_inherited else new_findings).append(finding)
    if new_findings:
        FINDINGS.extend({"stage": "new_public_file_privacy", **f} for f in new_findings)
    return {"result": "fail" if new_findings else "pass", "new_text_files_scanned": scanned,
            "new_file_findings": new_findings, "inherited_exact_byte_findings_not_silently_rewritten": inherited_findings,
            "policy": "Only sanitized relative filename, line and finding class are recorded; possible credential values and local operational path contents are never copied into this receipt.",
            "limit": "High-confidence token/assignment/private-path heuristics, not proof that every possible secret encoding is absent. Inherited provenance is separately classified by exact frozen hash."}


def checksum_qa():
    path = BASE / "CHECKSUMS.sha256"
    if not path.is_file():
        return {"result": "fail", "path": "CHECKSUMS.sha256", "reason": "final_checksum_inventory_not_present"}
    seen = set()
    for line in path.read_text("utf-8").splitlines():
        match = re.fullmatch(r'([0-9a-fA-F]{64})  ([^\r\n]+)', line)
        check(match is not None, "checksum inventory line syntax")
        expected, rel = match.groups()
        check(rel not in seen and rel not in {"CHECKSUMS.sha256", "qa/OFFLINE_REPLAY_PROGRESS.json"}, "unique non-self checksum inventory, no ephemeral progress")
        seen.add(rel)
        target = relative(rel)
        check(target.is_file(), "checksum target missing: " + rel)
        if target.resolve() == RECEIPT.resolve():
            continue
        check(digest(target.read_bytes()) == expected.lower(), "checksum byte identity: " + rel)
    required = {r["path"] for r in read_json(BASE / "INTAKE_MANIFEST.json")["files"]}
    required.update(p.relative_to(BASE).as_posix() for p in active_pages())
    required.update({"build.py", "validate_package.py", "assemble_support.py", "assemble_canon.py", "INTAKE_MANIFEST.json", "README.md", "LICENSE.md", "COVERAGE.json", "site.css", "support/practice.json", "canon/terminology.json", "qa/OFFLINE_REPLAY.json", "qa/OFFLINE_REPLAY_REPRODUCIBILITY.json"})
    required.update(r["path"] for r in read_json(BASE / "qa/OFFLINE_REPLAY.json")["exact_dependency_aliases"])
    required.update({"qa/PACKAGE_VALIDATION.json", "qa/b10-frontmatter-language-notes.md", "qa/b10-unit-001-language-notes.md", "qa/b10-unit-002-language-notes.md"})
    check(required <= seen, "checksum inventory covers required finite package files")
    return {"result": "pass", "path": "CHECKSUMS.sha256", "entries": len(seen),
            "required_files": len(required), "self_receipt_entry": "Deferred to final external package checksum/readback; the validator writes this receipt and cannot bind its own future bytes.",
            "inventory_hash_omitted": "Avoids checksum/validation-receipt hash cycles."}


def main():
    stages = {}
    functions = (("intake", intake_qa), ("source_seals", source_qa), ("active_pages", page_qa),
                 ("new_support_answers", support_qa), ("support_canon_replay", assembler_qa),
                 ("privacy", privacy_qa))
    for name, function in functions:
        if name == "source_seals" and stages["intake"]["result"] != "pass":
            stages[name] = {"result": "fail", "reason": "Frozen scripts not imported because intake verification failed."}
            continue
        try:
            stages[name] = function()
        except Exception as exc:
            # The error text may contain an absolute filesystem path. Do not
            # serialize it: known validation assertions use relative labels.
            message = str(exc) if isinstance(exc, AssertionError) else "See the named stage; exception details suppressed to avoid operational-path disclosure."
            message = message.replace(str(BASE), "<package>").replace(BASE.as_posix(), "<package>")
            stages[name] = {"result": "fail", "error_type": type(exc).__name__, "message": message}
            FINDINGS.append({"stage": name, "error_type": type(exc).__name__, "message": message})
    result = "pass" if all(s["result"] == "pass" for s in stages.values()) else "fail"
    record = {"schema": "b10.bounded-package-validation.v1", "result": result,
              "validator": ident(Path(__file__).resolve()), "stages": stages, "findings": FINDINGS,
              "assertions": CHECKS, "network_used": False, "git_used": False,
              "write_scope": "qa/PACKAGE_VALIDATION.json only; assembler writes intercepted in memory",
              "excluded_ephemeral_file": "qa/OFFLINE_REPLAY_PROGRESS.json",
              "checksum_policy": "Checksum verification runs after this deterministic receipt is written and is reported through stdout and process exit status. Its own state, entry count and inventory hash are deliberately absent here. The receipt's own checksum entry is checked only by the final external package inventory/readback.",
              "limits": ["Bounded opening only, not a complete textbook.", "No network citation checks, new rights determination, native-language certification, or visual/assistive-technology certification.", "Source replay receipts and live source/math/ID/hash seals are checked; unchanged source readers are not regenerated by this validation command.", "Final external checksum inventory and anonymous publication readback must bind the final bytes of this receipt itself."]}
    payload = (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    check(str(BASE).encode() not in payload and BASE.as_posix().encode() not in payload, "receipt has no package absolute path")
    RECEIPT.write_bytes(payload)
    try:
        checksum_result = checksum_qa()
    except Exception as exc:
        message = str(exc) if isinstance(exc, AssertionError) else "Checksum verification failed; exception detail suppressed."
        checksum_result = {"result": "fail", "error_type": type(exc).__name__, "message": message}
    overall = "pass" if result == "pass" and checksum_result["result"] == "pass" else "fail"
    print(json.dumps({"result": overall, "receipt_result": result, "receipt": ident(RECEIPT), "findings": FINDINGS, "checksum_verification": checksum_result}, ensure_ascii=False, indent=2))
    return 0 if overall == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
