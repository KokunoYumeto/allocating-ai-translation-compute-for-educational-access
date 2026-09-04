#!/usr/bin/env python3
"""Offline source-to-reader replay of the three recovered B10 checkpoints.

Run: python build.py
Dependencies: Python 3.10+, lxml, Pillow. No network, Git, TeX, Perl, PG,
browser, source checkout, or upstream executable is used.

The immutable frozen/ intake is the authority. Original renderers are imported
unchanged; their old-checkout loaders are explicitly replaced by the bounded
adapters below. Frontmatter/Chapter 0 use exact frozen XML excerpts. Section 1.1
reconstructs original file boundaries from the sealed 1,602-node source ledger,
then checks them against the separately retained XML/cache witnesses. Frozen
HTML is used ONLY as an exact comparator, never as generation input.

This is reproducible regeneration of the bounded readers from retained source
trees and frozen translations, not recreation or revalidation of an unavailable
whole Git checkout. Original full-file Git hashes remain historical assertions
unless their bytes are actually retained. No native-language approval, general
TeX support, newly generated WeBWorK variants, or whole-book completion is claimed.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
FROZEN = BASE / "frozen"
sys.path.insert(0, str(FROZEN / "scripts"))

from lxml import etree as E, html as LH
from PIL import Image

UNITS = ("b10-frontmatter", "b10-unit-001", "b10-unit-002")
RECEIPT = BASE / "qa/OFFLINE_REPLAY.json"
ROWS: dict[str, dict] = {}
ADAPTER_CHECKS: list[str] = []


def offline_audit(event, args):
    if event in {"subprocess.Popen", "os.system", "socket.connect", "socket.getaddrinfo"}:
        raise RuntimeError("Offline replay blocked external operation: " + event)
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name, mode, flags = args[:3]
        writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing and Path(os.fsdecode(name)).resolve().is_relative_to(FROZEN.resolve()):
            raise RuntimeError("Immutable frozen input write blocked")


sys.addaudithook(offline_audit)


def require(condition, message):
    if not condition:
        raise ValueError(message)
    ADAPTER_CHECKS.append(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text("utf-8"), object_pairs_hook=unique)


def jhash(value):
    return sha(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())


def identity(path):
    raw = path.read_bytes()
    return {"path": path.relative_to(BASE).as_posix(), "bytes": len(raw), "sha256": sha(raw)}


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def parse(raw):
    return E.fromstring(raw, E.XMLParser(remove_comments=True, resolve_entities=False, no_network=True))


def tree(node):
    return [node.tag, dict(node.attrib), node.text, [[tree(child), child.tail] for child in node]]


def forbid_external(*args, **kwargs):
    raise RuntimeError("Offline replay forbids Git/network/process execution")


def verify_intake():
    intake = read_json(BASE / "INTAKE_MANIFEST.json")
    require(intake["result"] == "pass" and intake["file_count"] == 53, "53-file intake identity")
    rows = intake["files"]
    require(len(rows) == 53 and len({r["path"] for r in rows}) == 53, "unique intake inventory")
    for row in rows:
        path = BASE / row["path"]
        require(path.resolve().is_relative_to(FROZEN.resolve()), "safe frozen path: " + row["path"])
        raw = path.read_bytes()
        require((len(raw), sha(raw)) == (row["bytes"], row["sha256"]), "exact frozen bytes: " + row["path"])
        ROWS[row["path"]] = row
    require(sum(r["bytes"] for r in rows) == intake["total_bytes"], "intake total bytes")
    return intake


def retained_notice_policy():
    manifest = read_json(FROZEN / "source-excerpts/manifest-b10-frontmatter.json")
    policy = manifest["existing_notice_policy"]
    # Identify retained notice bytes by their historical raw hash, not by the
    # unavailable old workspace path. The old path remains untouched evidence.
    for row in policy["notice_inputs"]:
        found = [r for r in ROWS.values() if r["sha256"] == row["raw_sha256"]]
        require(bool(found), "retained exact notice available: " + row["path"])
        for record in found:
            raw = (BASE / record["path"]).read_bytes()
            require(sha(raw.replace(b"\r\n", b"\n")) == row["logical_lf_sha256"], "notice logical-LF identity")
    current = copy.deepcopy(policy)
    current["components"] = "Current B10-002 contains six authored WeBWorK owners and six pinned static cache records: four remote OPL references and two local PG sources. Retain their component notices and exact identity evidence. No PreTeXt/Runestone runtime, grading or randomization is included."
    current["historical_scope_context"] = {
        "source_manifest": "source-excerpts/manifest-b10-frontmatter.json",
        "components_verbatim": policy["components"],
        "qualification": "The inherited zero-WeBWorK sentence concerned the earlier proposed opening/Chapter0, not B10-002. It is retained here solely as historical evidence and is not the current component inventory.",
    }
    return current


def check_authority(manifest):
    lock = read_json(FROZEN / "sources.lock.json")
    authority = manifest["authority"]
    if "lock_raw_sha256" in authority:
        require(sha((FROZEN / "sources.lock.json").read_bytes()) == authority["lock_raw_sha256"], "source-lock raw seal")
    for role, lockrole in (("canonical", "B10 upstream"), ("comparison", "B10")):
        actual = authority[role]
        expected = next(r for r in lock["repositories"] if r["role"] == lockrole)
        require((actual["commit"], actual["tree"], actual["local_path"], actual["repository"]) ==
                (expected["commit"], expected["tree"], expected["local_path"], expected["url"]),
                "historical authority/lock agreement: " + role)


def inputs(unit):
    m = read_json(FROZEN / ("source-excerpts/manifest-" + unit + ".json"))
    t = read_json(FROZEN / ("translations/" + unit + ".json"))
    raw = (FROZEN / ("source-excerpts/" + unit + ".ptx")).read_bytes()
    require((len(raw), sha(raw)) == (m["excerpt_bytes"], m["excerpt_sha256"]), unit + " exact source excerpt")
    source = parse(raw)
    require(jhash(tree(source)) == m["source_active_tree_sha256"], unit + " exact active source tree")
    require(t["locale"] == "pnb-Arab-PK", unit + " translation locale")
    check_authority(m)
    return m, t, source


def assets(manifest, frontmatter=False):
    prepared = []
    for spec in manifest["images" if frontmatter else "declared_assets"]:
        target = FROZEN / spec["planned_reader_path"]
        require(target.resolve().parent == (FROZEN / "assets/b10").resolve(), "bounded image path")
        raw = target.read_bytes()
        require((len(raw), sha(raw)) == (spec["bytes"], spec["sha256"]), "exact image bytes: " + spec["id"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == spec["git_blob_sha1"], "exact retained image Git blob: " + spec["id"])
        if frontmatter:
            with Image.open(target) as image:
                require(image.size == (spec["width"], spec["height"]), "PNG dimensions")
        else:
            svg = parse(raw)
            require((svg.get("width"), svg.get("height"), svg.get("viewBox")) ==
                    (spec["width"], spec["height"], spec["viewBox"]), "SVG dimensions")
            require(not any(v for n in svg.iter() for k, v in n.attrib.items() if k.endswith("href") and not v.startswith("#")), "SVG has no external dependency")
        prepared.append((spec, target, raw))
    return prepared


def simple_ledger(source, source_path):
    return [dict(path=source_path(n), tag=n.tag, attributes=dict(n.attrib),
                 children=[source_path(c) for c in n], own_text=n.text, tail=n.tail)
            for n in source.iter()]


def load_frontmatter():
    p = importlib.import_module("prepare_b10_frontmatter")
    m, t, source = inputs("b10-frontmatter")
    require(simple_ledger(source, p.source_path) == m["source_structure"], "frontmatter exact structure ledger")
    dmoi = copy.deepcopy(source)
    dmoi.remove(dmoi.find("docinfo"))
    dmoi.find("book").remove(dmoi.find("book/frontmatter"))
    roots = {"bookinfo.ptx": copy.deepcopy(source.find("docinfo")),
             "frontmatter.ptx": copy.deepcopy(source.find("book/frontmatter")), "dmoi.ptx": dmoi}
    require(p.source_keys(roots) == m["source_keys"] == list(t["source_blocks"]), "frontmatter exact 50-key order")
    require(len(m["source_keys"]) == 50, "frontmatter key count")
    require([n.get(p.XID) for n in source.iter() if n.get(p.XID)] == ["dmoi4", "frontmatter", "preface", "pref_editions"], "frontmatter source IDs")
    require(len(list(source.iter(p.XI))) == 1 and source.find(".//" + p.XI).attrib == {"href": "assets/tikz-defs.tex", "parse": "text"}, "inert source dependency retained")
    return m, t, source, roots, assets(m, True)


def load_001():
    p = importlib.import_module("prepare_b10_001")
    m, t, source = inputs("b10-unit-001")
    require(simple_ledger(source, p.source_path) == m["source_structure_ledger"], "Chapter 0 exact structure ledger")
    require([p.key(n) for n in source.iter() if n.tag in p.SLOT_TAGS] == m["expected_source_keys"] == list(t["source_blocks"]), "Chapter 0 exact 157-key order")
    require(len(m["expected_source_keys"]) == 157 and len(list(source.iter())) == 492, "Chapter 0 complete bounded scope")
    for seal in m["translation_block_seals"]:
        require(sha(t["source_blocks"][seal["key"]].encode()) == seal["sha256"], "Chapter 0 translation block seal")
    for field, seal in m["original_field_seals"].items():
        require(jhash(t[field]) == seal, "Chapter 0 original-field seal: " + field)
    nodes = {p.key(n): n for n in source.iter()}
    check_blocks(m, nodes)
    return m, t, source, assets(m)


def check_blocks(m, nodes):
    for block in m["source_blocks"]:
        require(jhash(tree(nodes[block["key"]])) == block["source_tree_sha256"], "source block tree seal")
        for slot in block["slots"]:
            node = nodes[slot["source_path"]]
            require(node.tag == slot["source_tag"] and dict(node.attrib) == slot["source_attributes"], "source slot tag/attributes")
            if slot["kind"] == "tex":
                require(node.text == slot["raw_tex"] and sha(node.text.encode()) == slot["tex_sha256"], "exact source TeX owner/hash")


def reconstruct_roots(m, p):
    # Each path identifies a node in one original file, before active XML
    # includes were expanded. Preserve all own text, tails, attributes and order.
    rows = [r for r in m["source_structure_ledger"] if not r["source_path"].startswith(p.CACHEFILE + "#")]
    nodes = {}
    for row in rows:
        node = E.Element(row["tag"], row["attributes"])
        node.text, node.tail = row["own_text"], row["tail"]
        require(row["source_path"] not in nodes, "unique authored ledger path")
        nodes[row["source_path"]] = node
    children = set()
    for row in rows:
        for child in row["child_paths"]:
            require(child in nodes and child not in children, "single ledger parent")
            nodes[row["source_path"]].append(nodes[child])
            children.add(child)
    roots = {}
    for row in rows:
        if row["source_path"] not in children:
            file, _ = row["source_path"].split("#", 1)
            require(file not in roots, "one selected root per original file")
            roots[file] = nodes[row["source_path"]]
    require(list(roots) == [p.CHAPTER, p.SECTION, "source/practice/logic-statements.ptx", "source/exercises/logic-statements.ptx"], "four selected authored file boundaries")
    return roots


def load_002():
    p = importlib.import_module("prepare_b10_002")
    m, t, excerpt = inputs("b10-unit-002")
    roots = reconstruct_roots(m, p)
    cache_raw = p.CACHE.read_bytes()
    require((len(cache_raw), sha(cache_raw)) == (m["cache_excerpt_bytes"], m["cache_excerpt_sha256"]), "exact cached XML bytes")
    cache = parse(cache_raw)
    require(len(cache) == 6 and [jhash(tree(c)) for c in cache] == m["cache_record_tree_sha256"], "six exact cache record trees")
    selected = list(roots.items()) + [(p.CACHEFILE, c.find("static")) for c in cache]
    nodes = {file + "#" + p.source_path(n): n for file, root in selected for n in root.iter()}
    keys = {node: key for key, node in nodes.items()}
    ledger = [dict(source_path=file + "#" + p.source_path(n), tag=n.tag,
                   attributes=dict(n.attrib), own_text=n.text, tail=n.tail,
                   child_paths=[file + "#" + p.source_path(c) for c in n])
              for file, root in selected for n in root.iter()]
    require(ledger == m["source_structure_ledger"] and len(ledger) == 1602, "exact reconstructed 1602-node ledger")
    require([keys[n] for file, root in selected for n in root.iter() if p.blockable(n)] == m["expected_source_keys"] == list(t["source_blocks"]), "Section 1.1 exact 559-key order")
    require(len(m["expected_source_keys"]) == 559, "Section 1.1 key count")
    for key, seal in m["translation_block_seals"].items():
        require(sha(t["source_blocks"][key].encode()) == seal, "Section 1.1 translation block seal")
    for note in t["original_notes"]:
        require(jhash(note) == m["original_note_seals"][note["id"]], "original source-error/clarification note seal")
    require(jhash(t["terminology_choices"]) == m["original_terms_seal"], "original terminology seal")
    require(m["declared_assets"] == [], "Section 1.1 source has no external images")
    check_blocks(m, nodes)
    witnesses = p.component_witnesses(m)
    raws = {row["repository_path"]: (FROZEN / row["local_path"]).read_bytes() for row in witnesses["files"]}
    for binding, record in zip(m["cached_static_bindings"], cache):
        owner = nodes[binding["owner"]]
        static, pg = record.find("static"), record.find("pg")
        require((record.get("ww-id"), record.get(p.XID), static.get("seed")) == (binding["cache_ww_id"], binding["cache_xml_id"], binding["seed"]), "cache owner/ID/seed binding")
        require(jhash(tree(static)) == binding["static_tree_sha256"] and sha((pg.text or "").encode()) == binding["inert_pg_text_sha256"], "exact cached static/PG seals")
        require(owner.get("source") == binding["source"], "authored cache reference")
        if binding["source"]:
            require(pg.get("source") == static.get("source") == binding["source"], "external cache source identity")
        else:
            require((pg.text or "").strip() == raws[binding["parse_text_source"]].decode().strip(), "inert local PG/cache byte witness")
    # The expanded excerpt independently supplies the full authored boundary.
    # Verify node tag/attribute and significant text order against the separately
    # reconstructed files, omitting only the two XML include wrappers and
    # whitespace introduced by the historical textual include operation.
    def expanded(node):
        if node.tag == p.XI and node.get("parse") != "text":
            yield from expanded(roots["source/" + node.get("href")])
            return
        yield node
        for child in node:
            yield from expanded(child)
        if node is roots[p.CHAPTER]:
            yield from expanded(roots[p.SECTION])
    def signature(node):
        return (node.tag, dict(node.attrib), (node.text or "").strip(), (node.tail or "").strip())
    require([signature(n) for n in expanded(roots[p.CHAPTER])] == [signature(n) for n in excerpt.iter()], "separate authored excerpt/ledger semantic-tree agreement")
    return m, t, roots, cache, nodes, keys, raws


def install_adapters():
    front = importlib.import_module("prepare_b10_frontmatter")
    front.git = forbid_external
    front.load_inputs = load_frontmatter
    one = importlib.import_module("prepare_b10_001")
    one.git = forbid_external
    one.load_inputs = load_001
    two = importlib.import_module("prepare_b10_002")
    two.git = forbid_external
    two.load_inputs = load_002
    two.retained_policy = retained_notice_policy
    return front, one, two


def mutation_tests(validate, root, notice):
    trials = []
    def trial(name, change):
        mutated, altered = copy.deepcopy(root), copy.deepcopy(notice)
        change(mutated, altered)
        try:
            validate(mutated, altered)
        except (AssertionError, ValueError, KeyError, IndexError, TypeError, E.XMLSyntaxError) as exc:
            trials.append({"name": name, "rejected_by": str(exc)})
        else:
            raise ValueError("Detached mutation was not rejected: " + name)
    trial("translated source block altered", lambda r, n: setattr(r.xpath('//*[@data-source-key]')[0], "text", "CHANGED"))
    trial("source node removed", lambda r, n: r.xpath('//*[@data-source-node]')[-1].getparent().remove(r.xpath('//*[@data-source-node]')[-1]))
    trial("source ID altered", lambda r, n: r.xpath('//*[@data-source-node and @id]')[0].set("id", "changed-source-id"))
    trial("executable script injected", lambda r, n: r.find("body").append(E.fromstring(b"<script>bad()</script>")))
    trial("source license changed", lambda r, n: n.update(source_specific_license="CHANGED"))
    if root.xpath('//*[@data-source-tex]'):
        trial("exact formula changed", lambda r, n: r.xpath('//*[@data-source-tex]')[0].set("data-source-tex", "999"))
        trial("derived MathML leaf changed", lambda r, n: setattr(r.xpath('//*[local-name()="math"]//*[local-name()="mi" or local-name()="mn" or local-name()="mo"]')[0], "text", "999"))
        trial("raw formula fallback altered", lambda r, n: setattr(r.xpath('//*[@data-source-tex-fallback]')[0], "text", "999"))
    if root.xpath('//*[@data-cache-record]'):
        trial("cache seed association changed", lambda r, n: r.xpath('//*[@data-cache-record]')[0].set("data-cache-owner", "wrong-owner"))
        trial("false cached parity warning removed", lambda r, n: r.xpath('//*[@class="cache-warning"]')[0].getparent().remove(r.xpath('//*[@class="cache-warning"]')[0]))
        trial("component witness attribution changed", lambda r, n: n["selected_component_witnesses"]["files"][1].update(source_header_verbatim="Unknown"))
    return trials


def structural_qa(prepares):
    results = []
    for unit, prep, suffix in zip(UNITS, prepares, ("frontmatter", "001", "002")):
        qa = importlib.import_module("qa_b10_" + suffix)
        output = BASE / ("reader/" + unit + ".html")
        qa.OUTPUT = output
        args = prep.load_inputs()
        notice = read_json(prep.NOTICES)
        raw = output.read_text("utf-8")
        if suffix == "frontmatter":
            root = qa.parse_html(raw)
            validate = lambda r, n: qa.validate(r, args[0], args[1], args[3], n, args[4])
        elif suffix == "001":
            root = qa.parse_reader(raw)
            validate = lambda r, n: qa.validate(r, args[0], args[1], args[2], n, args[3])
        else:
            root = E.fromstring(raw.replace("<!doctype html>", "").encode())
            qa.EXPECTED_NOTICE = prep.notice_record(args[0])
            validate = lambda r, n: qa.validate(r, args, n)
        checks = validate(root, notice)
        checks = len(checks) if isinstance(checks, list) else checks
        browser = LH.fromstring(raw)
        xmlnodes = root.xpath('//*[@data-source-node]')
        htmlnodes = browser.xpath('//*[@data-source-node]')
        require([n.get("data-source-node") for n in xmlnodes] == [n.get("data-source-node") for n in htmlnodes], unit + " browser parser source order")
        for xmlnode, htmlnode in zip(xmlnodes, htmlnodes):
            def parent_key(node):
                return next((p.get("data-source-node") for p in node.iterancestors() if p.get("data-source-node")), None)
            require(parent_key(xmlnode) == parent_key(htmlnode), unit + " browser parser ancestry")
            require(xmlnode.get("data-source-tex") == htmlnode.get("data-source-tex"), unit + " browser parser raw TeX")
        mutations = mutation_tests(validate, root, notice)
        results.append({"unit": unit, "result": "pass", "inherited_structural_math_checks": checks,
                        "source_nodes": len(xmlnodes), "source_keys": len(root.xpath('//*[@data-source-key]')),
                        "source_tex_owners": len(root.xpath('//*[@data-source-tex]')),
                        "derived_mathml": len(root.xpath('//*[local-name()="math"]')),
                        "detached_mutations_rejected": mutations,
                        "reader": identity(output)})
    return results


def mapper_qa():
    tests = {
        "001": {
            "unsupported": [r"\sqrt{x}", r"\input{file}", r"\write18{bad}", r"\unknown", r"f_{n-1", r"(a_n)_{n\ge0", r"\frac{n}{2", r"\text{and}", r"\text{ dan }", "x_10", "x^^2", "x/2", "", r"[0,\infty]"],
            "changed": [("f_4=3", "f_3=3"), (r"f(n)=2\cdot f(n-1)", r"f(n)=2\cdot f(n+1)"), (r"(a_n)_{n\ge0}", "a_n"), (r"a_n=\frac{n(n+1)}{2}", r"a_n=\frac{n(n+1)}{3}"), (r"[0,\infty)", r"(0,\infty)"), ("3^2+4^2=5^2", "3^2+4^2=6^2")],
        },
        "002": {
            "unsupported": [r"\frac{1}{2}", r"\input{secret}", r"\unknown", "x_1", "x^{2", "x^", "(x]", "[0,1)", "x^^2", r"\text{Maybe}", r"\text{True }", r"\!x", r"x\!y", "x^23", "", r"\forall{x", "x$y", r"\text{Choice {1}}"],
            "changed": [(r"\forall x P(x)", r"\exists x P(x)"), (r"P\wedge Q", r"P\vee Q"), (r"x\lt y", r"x\le y"), (r"\forall x\exists y P(x,y)", r"\exists x\forall y P(x,y)"), (r"\forall x\exists y(y^2=x)", r"\forall x\exists y(y^3=x)"), ("P(x,y)", "P(y,x)"), (r"\neg(P\wedge Q)\imp Q", r"\neg P\wedge Q\imp Q"), (r"\text{False}", r"\text{True}")],
        },
    }
    records = []
    for suffix, cases in tests.items():
        mapper = importlib.import_module("b10_" + suffix + "_tex")
        fixture = importlib.import_module("b10_" + suffix + "_math_expected")
        for bad in cases["unsupported"]:
            try:
                mapper.convert(bad)
            except mapper.TexError:
                pass
            else:
                raise ValueError("Unsupported mapper grammar accepted: " + repr(bad))
        for original, changed in cases["changed"]:
            require(mapper.convert(changed)[1]["tree"] != fixture.expected(original), "changed mathematical meaning rejected by independent fixture")
        records.append({"unit": "b10-unit-" + suffix, "result": "pass",
                        "unsupported_grammar_rejected": cases["unsupported"],
                        "plausible_changed_mathematics_detected": cases["changed"]})
    return records


def reader_link_qa():
    rows = []
    for unit in UNITS:
        path = BASE / ("reader/" + unit + ".html")
        root = LH.fromstring(path.read_text("utf-8"))
        count, external = 0, 0
        for node in root.xpath('//*[@href or @src]'):
            reference = node.get("href") if node.get("href") is not None else node.get("src")
            parts = urlsplit(reference)
            if parts.scheme or parts.netloc:
                require(parts.scheme in {"http", "https", "mailto"}, "no executable URL scheme")
                external += 1
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path.resolve()
            require(target.is_relative_to(BASE.resolve()), "relative reader dependency stays inside package")
            require(target.is_file(), "relative reader dependency exists: " + reference)
            if parts.fragment and target.suffix == ".html":
                linked = root if target == path.resolve() else LH.fromstring(target.read_text("utf-8"))
                require(unquote(parts.fragment) in linked.xpath('//@id'), "relative reader HTML fragment resolves")
            count += 1
        rows.append({"unit": unit, "result": "pass", "local_references_checked": count,
                     "external_attribution_links_retained_not_fetched": external})
    return rows


def main():
    intake = verify_intake()
    retained_notice_policy()
    prepares = install_adapters()
    (BASE / "reader").mkdir(exist_ok=True)
    (BASE / "qa").mkdir(exist_ok=True)
    alias_prefixes = ("frozen/assets/", "frozen/source-excerpts/", "frozen/provenance/")
    for row in intake["files"]:
        if row["path"].startswith(alias_prefixes):
            target = BASE / row["path"].removeprefix("frozen/")
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = (BASE / row["path"]).read_bytes()
            require(not target.exists() or target.read_bytes() == raw, "refuse replacement of changed reader dependency: " + target.relative_to(BASE).as_posix())
            if not target.exists():
                target.write_bytes(raw)
    replay = []
    for pass_number in (1, 2):
        pass_rows = []
        for unit, suffix in zip(UNITS, ("frontmatter", "001", "002")):
            builder = importlib.import_module("build_b10_" + suffix)
            builder.OUTPUT = BASE / ("reader/" + unit + ".html")
            expected = FROZEN / ("reader/" + unit + ".html")
            require(not builder.OUTPUT.exists() or builder.OUTPUT.read_bytes() == expected.read_bytes(), "refuse replacement of changed existing reader: " + unit)
            builder.build()
            require(builder.OUTPUT.read_bytes() == expected.read_bytes(), unit + " generated reader exactly equals frozen comparator")
            pass_rows.append(identity(builder.OUTPUT))
        replay.append(pass_rows)
    require(replay[0] == replay[1], "two deterministic source-to-reader replays are byte-identical")
    progress = {"schema": "recovered-b10-offline-source-replay-progress.v1", "stage": "source_replay_complete",
                "replay_count": 2, "replays": replay, "next_action": "Run in-memory structural/math/mutation QA and seal the final receipt.",
                "build_script": identity(Path(__file__).resolve())}
    (BASE / "qa/OFFLINE_REPLAY_PROGRESS.json").write_bytes(json_bytes(progress))
    mapper_results = mapper_qa()
    qa = structural_qa(prepares)
    links = reader_link_qa()
    verify_intake()
    receipt = {
        "schema": "recovered-b10-offline-source-replay.v1", "result": "pass",
        "method": "unchanged frozen renderers with explicit offline source-tree loader adapters",
        "frozen_html_used_as": "post-generation exact byte comparator only; never generation input",
        "source_reconstruction": {
            "b10-frontmatter": "Exact frozen source excerpt, active-tree and full structure-ledger seals; original docinfo/frontmatter file roots reconstructed without content changes.",
            "b10-unit-001": "Exact frozen expanded Chapter 0 excerpt; 492-node structure and 157-key/translation/block/tree/TeX seals.",
            "b10-unit-002": "Four authored source-file roots reconstructed from sealed 1602-node ledger; exact own text, tails, attributes and child order. Exact six XML-cache trees and seven PG/license byte/blob witnesses; expanded authored excerpt checked independently.",
        },
        "intake": identity(BASE / "INTAKE_MANIFEST.json"),
        "frozen_file_count": intake["file_count"], "frozen_bytes": intake["total_bytes"],
        "frozen_inputs_unchanged_after_replay": True,
        "build_script": identity(Path(__file__).resolve()),
        "replay_count": 2, "replays": replay, "units": qa,
        "finite_mapper_tests": mapper_results,
        "reader_dependency_closure": links,
        "adapter_assertions": len(ADAPTER_CHECKS),
        "assets": [identity(BASE / r["path"].removeprefix("frozen/")) for r in intake["files"] if r["path"].startswith("frozen/assets/")],
        "exact_dependency_aliases": [identity(BASE / r["path"].removeprefix("frozen/")) for r in intake["files"] if r["path"].startswith(alias_prefixes)],
        "limitations": [
            "No old Git checkout is required or inspected. Historical commit/tree declarations are cross-checked against the sealed source lock, not independently revalidated against a complete Git object database.",
            "Selected source tree/hash seals are rechecked; unretained original whole-file byte formatting, comments, comparison inputs and inactive dependency blobs are not reconstructed or claimed newly verified.",
            "Finite observed TeX grammar only: 441 derived MathML owners and one intentionally preserved visible raw-TeX fallback across the two instructional units; no TeX engine executes.",
            "Six WeBWorK caches are fixed source snapshots; no PG is executed, no variants generated, no answers invented and no online grading implemented. Source-error warnings and supplied source answers remain unchanged.",
            "Structural exactness is not independent linguistic or accessibility certification; whole B10/book/five-work completion is not claimed.",
            "Browser DOM parsing is checked; visual/browser/assistive-technology QA is a separate release-package check.",
        ],
        "network_used": False, "git_used": False, "upstream_execution": False,
        "enforcement": "Python audit hook rejects subprocesses, shell execution, socket connection/DNS and writes to frozen/; original Git helpers additionally fail closed.",
    }
    RECEIPT.write_bytes(json_bytes(receipt))
    failure_path = BASE / "qa/OFFLINE_REPLAY_FAILURE.json"
    if failure_path.is_file():
        failure_path.unlink()
    print(json.dumps({"result": "pass", "receipt": identity(RECEIPT), "readers": replay[-1], "checks": [r["inherited_structural_math_checks"] for r in qa]}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        failure = {"schema": "recovered-b10-offline-source-replay-failure.v1", "result": "fail",
                   "error_type": type(error).__name__, "error": str(error),
                   "completed_adapter_assertions": len(ADAPTER_CHECKS),
                   "next_action": "Correct only the offline adapter or supply the precisely missing in-scope support file; keep frozen input bytes unchanged."}
        (BASE / "qa").mkdir(exist_ok=True)
        (BASE / "qa/OFFLINE_REPLAY_FAILURE.json").write_bytes(json_bytes(failure))
        raise
