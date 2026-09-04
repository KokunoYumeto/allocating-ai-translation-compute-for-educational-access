#!/usr/bin/env python3
"""B40 opening INPUT QA only. No preparer/renderer imports or TeX execution.

Independent finite source-span/table/slot discovery plus explicit nonlinguistic
contracts. Reviewed Punjabi block seals detect later edits; they do NOT prove
translation quality or the mathematical validity of a future MathML converter.
Only this script's deterministic small JSON receipt is written.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
LOCALE = ROOT / "languages/pnb-Arab-PK"
MANIFEST = LOCALE / "source-excerpts/manifest-b40-opening.json"
TRANSLATION = LOCALE / "translations/b40-opening.json"
WITNESS = LOCALE / "source-excerpts/b40-opening.json"
RECEIPT = LOCALE / "qa/structural-b40-opening-inputs.json"
EN_PIN = "df2262e089a02651c127f1dd12649c4622ee1383"
ID_PIN = "e84ce2956a7304830c42eba70106f940fefee7c4"
SY = "src/cover/symlist.tex"
PF = "src/pref/pref.tex"
ORDER = ["src/cover/covernew.tex", "src/sty/covergraphic.sty",
         "src/publicationdate.tex", SY, PF]
RAW_FILES = ["book.tex", "cover/covernew.tex", "cover/symlist.tex",
             "pref/pref.tex", "sty/covergraphic.sty", "publicationdate.tex"]
EN_HASH = dict(zip(RAW_FILES, [
    "5493db2d10853ad7fdce70b4e6cc65174b7dbb3a66d8d654782977e7137abaaa",
    "efaabdd0823dec1d89db66ae61b369ccbbe71d0b4a8dcc103da372ef279b78b9",
    "01dbeee390674cd31e3e34c2f6cee9089124c0d0e363ab4449f8874358efc6e4",
    "3da93c7c1bc80e8b5012471418f7e06bfc969097c1455fadcc570511847697e6",
    "c5321d1fc20073bf5aff7fd1b93e7da916e241f33d0a0c313a75df96f4191f8c",
    "a7ea5cfcd6407980af46ba8934ab5f4f1b2af07483e81098e9d6e956e8389101"]))
ID_HASH = dict(zip(RAW_FILES, [
    "a260d6dc1036c61644cc8ae3522b17924a943dd3d8f7209576b7bc8e72b95b8b",
    "3b4555c37a4f551fdac76bb99f25f44cff6b00a2885fc027d6a9ef8e2e41c8d3",
    "1defc2a8b40959e75cd293133c993de8f9c9e2c3607b2a90b1dad9903a6814de",
    "ba37b47cc122afb1d4c1fa0f69fba3c2a4be893e0c2195e714f444a306eb1193",
    "d3eb06ce34ca8bf609308b770a16d045cf51d62950c43527752cbb204e3752bf",
    "8890e730fa85c8cf06ead42b767140eba0324dc5f8808f11472d822bfb7bb389"]))
# Independent page-text boundaries actually read in the canonical full preface.
PREF_LINES = [(6, 7), (9, 19), (21, 39), (41, 49), (51, 66), (68, 81),
              (83, 88), (98, 110), (117, 125), (131, 137), (139, 141),
              (145, 145), (158, 161), (163, 168), (211, 221), (223, 225),
              (227, 232), (234, 241), (243, 253), (294, 301)]
SHAPES = [(SY, 1, 20, 2), (SY, 2, 13, 4), (PF, 1, 15, 2),
          (PF, 2, 4, 1), (PF, 3, 5, 1), (PF, 4, 7, 1)]
NOTES = ["b40-opening-author-context", "b40-opening-degree-qualification",
         "b40-opening-natural-convention", "b40-opening-pronunciation-context",
         "b40-opening-scope"]
TOKEN = re.compile(r"\{\{(?:tex|url|include|mark):\d+\}\}")
REF = re.compile(r"(?:One|Two|Three|Four|Five)\.[IVX]+(?:\.\d+(?:(?:--|–)\d+)?)?")
COMMENT = re.compile(r"(?<!\\)%[^\n]*(?:\n|$)")


def sha(raw):
    return hashlib.sha256(raw.encode("utf-8") if isinstance(raw, str) else raw).hexdigest()


def jsha(obj):
    return sha(json.dumps(obj, ensure_ascii=False, separators=(",", ":")))


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def active(raw):
    return COMMENT.sub("", raw)


def mask(raw):
    """Comments consume newline, but keep absolute indices usable for discovery."""
    return COMMENT.sub(lambda m: " " * len(m.group()), raw)


class Failure(AssertionError):
    pass


class Check:
    def __init__(self):
        self.count = 0

    def eq(self, actual, expected, label):
        self.count += 1
        if actual != expected:
            raise Failure(label)

    def yes(self, condition, label):
        self.eq(bool(condition), True, label)


def braced(text, pos):
    if pos >= len(text) or text[pos] != "{":
        raise Failure("discovery.required-group")
    depth = 1
    i = pos + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if not depth:
                return pos + 1, i, i + 1
        i += 1
    raise Failure("discovery.unclosed-group")


def trimmed(text, start, end):
    view = mask(text[start:end])
    a = len(view) - len(view.lstrip())
    b = len(view.rstrip())
    return start + a, start + b


def table_spans(text):
    """Independent brace-aware active tabular scanner; no generic TeX evaluator."""
    view = mask(text)
    out = []
    for found in re.finditer(r"\\begin\{tabular\}(?:\[[^]]+\])?", view):
        _, _, body = braced(view, found.end())
        end = view.index(r"\end{tabular}", body)
        i, start, depth = body, body, 0
        row, rows = [], []
        def flush_cell(stop):
            nonlocal start, row
            # A row-level hline is layout, not a source cell.
            a, b = trimmed(text, start, stop)
            if view.startswith(r"\hline", a):
                a, b = trimmed(text, a + len(r"\hline"), b)
            if a < b:
                row.append((a, b))
        while i < end:
            if view.startswith(r"\\", i) and depth == 0:
                flush_cell(i)
                if row:
                    rows.append(row)
                row = []
                i += 2
                if i < end and view[i] == "[":
                    i = view.index("]", i) + 1
                start = i
                continue
            ch = view[i]
            if ch == "\\":
                i += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    raise Failure("discovery.table-group")
            elif ch == "&" and depth == 0:
                flush_cell(i)
                start = i + 1
            i += 1
        flush_cell(end)
        if row:
            rows.append(row)
        if depth:
            raise Failure("discovery.table-depth")
        out.append(rows)
    return out


def discover_sources(files):
    found = []
    def add(file, suffix, kind, start, end, **extra):
        found.append(dict(key=file + "#" + suffix, kind=kind, source_file=file,
                          source_start=start, source_end=end, **extra))
    def literal(file, suffix, kind, needle):
        view = mask(files[file])
        matches = list(re.finditer(re.escape(needle), view))
        if len(matches) != 1:
            raise Failure("discovery.literal-unique:" + suffix)
        hit = matches[0]
        add(file, suffix, kind, hit.start(), hit.end())
    cv = "src/cover/covernew.tex"
    literal(cv, "metadata/title", "metadata", "Linear Algebra")
    literal(cv, "metadata/author", "metadata", "Jim Hef{}feron")
    cg = "src/sty/covergraphic.sty"
    for name, raw in [("title", "LINEAR ALGEBRA"), ("author", "Jim Hef{}feron"),
                      ("edition", "Fourth edition"), ("webaddress", "hefferon.net/linearalgebra")]:
        literal(cg, "visible/" + name, "cover-label", raw)
    literal("src/publicationdate.tex", "date", "publication-date", "2021-Oct-12")
    for i, raw in enumerate(["Notation", "Greek letters with pronounciation"], 1):
        literal(SY, f"heading/{i}", "heading", raw)
    literal(SY, "capitals-note", "prose",
            "Capitals shown are the ones that differ from Roman capitals.")
    for i, raw in enumerate(["Preface", "Applications.", "Availability.",
                             "Acknowledgments.", "Advice.", "Author's Note."], 1):
        literal(PF, f"heading/{i}", "heading", raw)
    lines = files[PF].splitlines(keepends=True)
    for i, (first, last) in enumerate(PREF_LINES, 1):
        a, b = trimmed(files[PF], sum(map(len, lines[:first - 1])), sum(map(len, lines[:last])))
        add(PF, f"paragraph/{i}", "prose", a, b)
    for file in [SY, PF]:
        for tn, rows in enumerate(table_spans(files[file]), 1):
            for rn, row in enumerate(rows, 1):
                for cn, (a, b) in enumerate(row, 1):
                    kind = "table-cell" if file == SY or tn == 1 else (
                        "author-credit" if tn == 4 else "lineated-quote")
                    add(file, f"table/{tn}/row/{rn}/cell/{cn}", kind, a, b,
                        table=tn, row=rn, column=cn)
    return sorted(found, key=lambda x: (ORDER.index(x["source_file"]), x["source_start"]))


def discover_slots(raw, file_start):
    """Raw source owner/offsets are discovered again; no TeX is interpreted."""
    view = mask(raw)
    out, counter = [], {}
    i = 0
    while i < len(view):
        start, kind, value, delimiters, end = i, None, None, None, None
        if view.startswith(r"\(", i):
            end = view.index(r"\)", i + 2) + 2
            kind, value, delimiters = "tex", raw[i + 2:end - 2], [r"\(", r"\)"]
        elif view[i] == "$" and (i == 0 or view[i - 1] != "\\"):
            end = i + 1
            while end < len(view) and (view[end] != "$" or view[end - 1] == "\\"):
                end += 1
            if end == len(view):
                raise Failure("slot.unclosed-dollar")
            end += 1
            kind, value, delimiters = "tex", raw[i + 1:end - 1], ["$", "$"]
        else:
            hit = re.match(r"\\(url|input)\{", view[i:])
            if hit:
                a, b, end = braced(raw, i + hit.end() - 1)
                kind = "url" if hit.group(1) == "url" else "include"
                value = raw[a:b]
            else:
                hit = re.match(r"\\(puzzlemark|recommendationmark)\b", view[i:])
                if hit:
                    end = i + hit.end()
                    kind, value = "mark", hit.group(1)
        if kind:
            n = counter.get(kind, 0)
            counter[kind] = n + 1
            out.append(dict(kind=kind, token="{{" + kind + ":" + str(n) + "}}",
                            value=value, delimiters=delimiters, raw=raw[start:end],
                            block_start=start, block_end=end,
                            file_start=file_start + start, file_end=file_start + end))
            i = end
        else:
            i += 1
    return out


def fragment(value, ck, label, original=False):
    ck.yes("<!" not in value and "<?" not in value, "html.no-comments:" + label)
    try:
        root = ET.fromstring("<fragment>" + value + "</fragment>")
    except ET.ParseError as exc:
        raise Failure("html.parse:" + label) from exc
    for node in list(root.iter())[1:]:
        allowed = {"bdi", "em", "span"} | ({"p"} if original else set())
        ck.yes(node.tag in allowed, "html.tag:" + label)
        if node.tag == "bdi":
            ck.yes(node.attrib in ({"dir": "ltr"}, {"dir": "ltr", "lang": "en"}),
                   "html.bdi-attrs:" + label)
            ck.eq(len(node), 0, "html.bdi-leaf:" + label)
        elif node.tag == "span":
            ck.eq(set(node.attrib), {"class", "data-source-pronunciation"},
                  "html.span-attrs:" + label)
            ck.eq(node.get("class"), "source-pronunciation", "html.span-class:" + label)
        else:
            ck.eq(node.attrib, {}, "html.plain-attrs:" + label)
    # Every literal Latin letter/digit in translated source prose must be LTR;
    # exact token placeholders are resolved later, never executed.
    def walk(node, isolated=False):
        inside = isolated or node.tag == "bdi"
        for text in [node.text or ""]:
            if not inside:
                ck.yes(not re.search(r"[A-Za-z0-9]", TOKEN.sub("", text)),
                       "html.literal-isolation:" + label)
        for child in node:
            walk(child, inside)
            if not inside:
                ck.yes(not re.search(r"[A-Za-z0-9]", TOKEN.sub("", child.tail or "")),
                       "html.tail-isolation:" + label)
    walk(root)
    return root


def flatten(node):
    return "".join(node.itertext())


def build_context(manifest):
    """Read exact local commit objects and working LF files; no network/engine."""
    ck, files, rawfiles = Check(), {}, {}
    for role, pin in [("canonical", EN_PIN), ("comparison", ID_PIN)]:
        record = manifest[role]
        ck.eq(record["commit"], pin, "pin.commit:" + role)
        repo = ROOT / record["local_path"]
        expected_repo = ROOT / ("downloads/upstream/hefferon-linear-algebra"
                                if role == "canonical" else "downloads/hefferon-linear-algebra-id")
        ck.eq(repo, expected_repo, "pin.repo:" + role)
        tree = subprocess.check_output(["git", "-C", str(repo), "rev-parse", pin + "^{tree}"]).decode().strip()
        ck.eq(tree, record["tree"], "pin.tree:" + role)
        for item in manifest["source_files"][role]:
            path = item["repository_path"]
            raw = subprocess.check_output(["git", "-C", str(repo), "show", pin + ":" + path])
            ck.eq(sha(raw), item["sha256"], "pin.sha:" + path)
            ck.eq(len(raw), item["bytes"], "pin.bytes:" + path)
            ck.eq(blob(raw), item["git_blob_sha1"], "pin.blob:" + path)
            work = (repo / path).read_bytes()
            ck.eq(sha(work), item["working_raw_sha256"], "pin.working-raw:" + path)
            ck.eq(work.replace(b"\r\n", b"\n"), raw, "pin.working-LF:" + path)
            rawfiles[(role, path)] = raw
            files[(role, path)] = raw.decode("utf-8")
        for tail, digest in (EN_HASH if role == "canonical" else ID_HASH).items():
            path = ("src/" if role == "canonical" else "source/linear-algebra/src/") + tail
            ck.eq(sha(rawfiles[(role, path)]), digest, "pin.independent:" + path)
    evidence = manifest["later_source_clarification_evidence"]
    path = evidence["repository_path"]
    repo = ROOT / manifest["canonical"]["local_path"]
    later = subprocess.check_output(["git", "-C", str(repo), "show", EN_PIN + ":" + path])
    ck.eq(sha(later), "d7b83def8532ee79706496b1a601f2ccf2f6c4d25231677aecd36b14cfae395d",
          "pin.later-definition")
    assetraw = {a["repository_path"]: subprocess.check_output(
        ["git", "-C", str(repo), "show", EN_PIN + ":" + a["repository_path"]])
        for a in manifest["source_assets"]}
    return dict(files=files, rawfiles=rawfiles, later=later, assets=assetraw, pin_checks=ck.count)


def validate(m, t, w, context, seals=True):
    ck = Check()
    en = {path: val for (role, path), val in context["files"].items() if role == "canonical"}
    ck.eq(m["canonical"]["commit"], EN_PIN, "input.canonical")
    ck.eq(m["comparison"]["commit"], ID_PIN, "input.comparison")
    ck.eq(m["source_files"], context["frozen_source_files"], "input.source-file-ledger")
    ck.eq(m["source_plan_sha256"], sha((LOCALE / m["source_plan"]).read_bytes()), "input.plan-hash")
    ck.eq(m["locale"], "pnb-Arab-PK", "input.locale")
    ck.eq(t["locale"], "pnb-Arab-PK", "input.target-locale")
    expected_witness = [(role, ("src/" if role == "canonical" else "source/linear-algebra/src/") + tail)
                        for role in ["canonical", "comparison"] for tail in RAW_FILES]
    ck.eq([(f["role"], f["repository_path"]) for f in w["files"]], expected_witness,
          "witness.files-order")
    for f in w["files"]:
        ck.eq(f["text"], context["files"][(f["role"], f["repository_path"])], "witness.exact-text")
    ck.eq(w["schema"], "pnb-b40-inert-raw-source-witness-v1", "witness.inert-schema")
    for flag in ["whole_frontmatter_complete", "whole_book_translation_complete"]:
        ck.eq(m[flag], False, "scope.manifest:" + flag)
        ck.eq(t[flag], False, "scope.translation:" + flag)
    ck.eq(m["whole_assignment_complete"], False, "scope.assignment")
    independent = discover_sources(en)
    ck.eq(len(independent), 174, "scope.independent174")
    keys = [r["key"] for r in independent]
    ck.eq([r["key"] for r in m["source_blocks"]], keys, "scope.manifest-keys-order")
    ck.eq(m["expected_source_keys"], keys, "scope.explicit-keys-order")
    ck.eq(list(t["source_blocks"]), keys, "scope.target-keys-order")
    ck.eq([(d["file"], d["number"], d["rows"], d["columns"]) for d in m["table_layouts"]],
          SHAPES, "table.layouts")
    ck.eq(sum(r * c for _, _, r, c in SHAPES), 138, "table.cells138")
    html_nodes, total_slots = {}, []
    for declared, expected in zip(m["source_blocks"], independent):
        key = expected["key"]
        for name in expected:
            ck.eq(declared[name], expected[name], "source.span." + name + ":" + key)
        raw = en[declared["source_file"]][expected["source_start"]:expected["source_end"]]
        ck.eq(declared["source_raw"], raw, "source.raw:" + key)
        ck.eq(declared["source_raw_sha256"], sha(raw), "source.raw-hash:" + key)
        ck.eq(declared["source_line"], en[declared["source_file"]].count("\n", 0, expected["source_start"]) + 1,
              "source.line:" + key)
        ck.eq(declared["active_tex"], active(raw), "source.active-comments:" + key)
        comparison = declared["comparison"]
        comp_raw = context["files"][("comparison", comparison["source_file"])][comparison["start"]:comparison["end"]]
        ck.eq(comparison["raw"], comp_raw, "source.comparison-span:" + key)
        ck.eq(comparison["raw_sha256"], sha(comp_raw), "source.comparison-hash:" + key)
        ck.eq(comparison, context["frozen_comparison"][key], "source.comparison-owner:" + key)
        slots = discover_slots(raw, declared["source_start"])
        ck.eq(declared["slots"], slots, "source.exact-slots:" + key)
        total_slots.extend(slots)
        target = t["source_blocks"][key]
        ck.eq(TOKEN.findall(target), [s["token"] for s in slots], "target.slot-order:" + key)
        ck.yes(not re.search(r"\{\{|\}\}", TOKEN.sub("", target)), "target.no-unknown-slot:" + key)
        ck.yes("\n" not in target and "\r" not in target, "target.no-invented-linebreak:" + key)
        node = fragment(target, ck, key)
        html_nodes[key] = node
        guides = re.findall(r"\\pronounced\{([^{}]+)\}", raw)
        spans = list(node.iter("span"))
        ck.eq([s.get("data-source-pronunciation") for s in spans], guides, "target.guide-source:" + key)
        for span, guide in zip(spans, guides):
            expected_words = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)*", guide)
            expected_words = [x for x in expected_words if x not in {"as", "in", "or"}]
            ck.eq([flatten(b) for b in span.iter("bdi")], expected_words,
                  "target.guide-words:" + key)
        # Every source-defined emphasis in an own-content slot is retained.
        expected_em = len(re.findall(r"\\(?:emph|textit)\{", raw))
        ck.eq(len(list(node.iter("em"))), expected_em, "target.emphasis:" + key)
        # Source section identifiers, including every week-range digit, are not translated.
        source_refs = REF.findall(raw)
        ck.eq(REF.findall(flatten(node)), [r.replace("--", "–") for r in source_refs],
              "target.section-references:" + key)
        if declared["source_file"] == SY and declared.get("column") in {1, 3}:
            # Only the source word 'or' may be localized in these pure-math cells.
            if slots:
                expected_tokens = ", ".join(s["token"] for s in slots)
                if key == SY + "#table/1/row/17/cell/1":
                    expected_tokens = "{{tex:0}} یا {{tex:1}}, {{tex:2}} یا {{tex:3}}"
                ck.eq(target, expected_tokens, "target.pure-math-cell:" + key)
        if seals:
            ck.eq(sha(target), m["input_seals"]["translation_block_seals"][key],
                  "reviewed.target-seal:" + key)
    ck.eq({kind: sum(s["kind"] == kind for s in total_slots) for kind in ["tex", "url", "include", "mark"]},
          {"tex": 76, "url": 3, "include": 1, "mark": 2}, "source.slot-counts")
    ck.eq(sum(len(list(n.iter("span"))) for n in html_nodes.values()), 24, "target.guides24")
    for week in range(1, 15):
        key = PF + f"#table/1/row/{week+1}/cell/1"
        ck.eq(t["source_blocks"][key], f'<bdi dir="ltr">{week}</bdi>', "target.week:" + str(week))
    for row in [7, 13, 14]:
        key = PF + f"#table/1/row/{row}/cell/2"
        value = flatten(html_nodes[key])
        ck.eq(value.count("–"), 2, "target.classday-en-dashes")
        ck.yes("—" not in value and "−" not in value and "--" not in value,
               "target.classday-not-minus")
    exact_credit = {
        "src/cover/covernew.tex#metadata/author": "Jim Hefferon",
        "src/sty/covergraphic.sty#visible/author": "Jim Hefferon",
        "src/sty/covergraphic.sty#visible/webaddress": "hefferon.net/linearalgebra",
        "src/publicationdate.tex#date": "2021-Oct-12",
        PF + "#table/2/row/4/cell/1": "–Stephen Jay Gould",
        PF + "#table/3/row/5/cell/1": "–Wilbur Wright",
        PF + "#table/4/row/1/cell/1": "Jim Hefferon",
        PF + "#table/4/row/3/cell/1": "Saint Michael's College",
        PF + "#table/4/row/4/cell/1": "Colchester, Vermont USA 05439",
        PF + "#table/4/row/5/cell/1": "{{url:0}}",
        PF + "#table/4/row/6/cell/1": "{{include:0}}"}
    for key, expected in exact_credit.items():
        ck.eq(flatten(html_nodes[key]), expected, "target.credit:" + key)
    for n, name in [(11, "Saint Michael's College"), (12, "Lynne"), (14, "G Ashline")]:
        bdis = [flatten(b) for b in html_nodes[PF + f"#paragraph/{n}"].iter("bdi")]
        ck.yes(name in bdis, "target.preface-name:" + name)
    ck.eq(t["source_blocks"]["src/sty/covergraphic.sty#visible/edition"], "چوتھا ایڈیشن",
          "target.fourth-edition")
    ck.eq(t["source_blocks"][PF + "#table/4/row/7/cell/1"], "چوتھا ایڈیشن، دوجی چھپائی",
          "target.second-printing")
    # Metadata and next required content are source evidence, not resolved today/generated TOC.
    ck.yes(r"\date{\today}" in active(en["src/cover/covernew.tex"]), "source.inert-today")
    outside = m["boundary"]["first_outside"]
    ck.eq(outside["file"], "src/book.tex", "scope.outside-file")
    ck.eq(outside["line"], 51, "scope.outside-line")
    ck.eq(active(en["src/book.tex"].splitlines(keepends=True)[50]).strip(), outside["source"],
          "scope.exact-outside")
    ck.yes(r"\boolfalse{hardcopybool}" in active(en["src/sty/bookjhconcrete.sty"]),
           "scope.default-cover")
    for n in [5, 6, 15]:
        record = next(b for b in m["source_blocks"] if b["key"] == PF + f"#paragraph/{n}")
        ck.yes("%" in record["source_raw"], "source.comment-bearing-paragraph")
        ck.yes("\n\n" not in active(record["source_raw"]), "source.comment-not-break")
    ck.eq(m["retained_notices"]["selected_license"], "CC-BY-SA-2.5", "notice.distinct-license")
    ck.eq(m["retained_notices"], context["plan"]["existing_notice_policy"], "notice.existing-retained")
    for record in m["retained_notices"]["inputs"]:
        raw = (LOCALE / record["path"]).read_bytes()
        ck.eq(sha(raw), record["raw_sha256"], "notice.raw-hash")
        ck.eq(sha(raw.replace(b"\r\n", b"\n")), record["logical_lf_sha256"], "notice.LF-hash")
    ck.eq(m["source_assets"], context["plan"]["assets"], "asset.plan")
    ck.eq(len(t["original_accessibility_alts"]), 2, "asset.two-alts")
    for asset, alt in zip(m["source_assets"], t["original_accessibility_alts"]):
        path = asset["repository_path"]
        raw = context["assets"][path]
        ck.eq(sha(raw), asset["sha256"], "asset.sha")
        ck.eq(len(raw), asset["bytes"], "asset.bytes")
        ck.eq(blob(raw), asset["git_blob_sha1"], "asset.blob")
        ck.eq((ROOT / m["canonical"]["local_path"] / path).read_bytes(), raw, "asset.working-exact")
        ck.eq(alt["repository_path"], path, "asset.alt-owner")
        ck.eq(alt["source_sha256"], sha(raw), "asset.alt-sha")
        ck.eq(alt["source_alt"], None, "asset.no-fabricated-source-alt")
        ck.eq(alt["origin"], "original-accessibility-description", "asset.original-alt")
        ck.yes(bool(alt["alt_pnb"]), "asset.nonempty-alt")
    cg = active(en["src/sty/covergraphic.sty"])
    ck.eq(re.findall(r"\\includegraphics\{([^{}]+)\}", cg),
          ["cover/asy/shadow.pdf", "cover/asy/axesgraphic.pdf"], "asset.source-layer-order")
    ck.yes(r"\put(-0.0,-6.9){\includegraphics{cover/asy/shadow.pdf}}" in cg, "asset.shadow-offset")
    ck.yes(r"\put(0,-6.5){\includegraphics{cover/asy/axesgraphic.pdf}}" in cg, "asset.planes-offset")
    ck.eq([n["id"] for n in t["original_notes"]], NOTES, "notes.order-and-count")
    for note in t["original_notes"]:
        ck.yes(note["kind"].startswith("original-"), "notes.origin")
        ck.yes(all(k in keys for k in note["source_keys"]), "notes.source-targets")
        ck.yes(note["id"] not in keys, "notes.not-source")
        fragment(note["html"], ck, note["id"], original=True)
        ck.yes(not TOKEN.search(note["html"]), "notes.no-source-tokens")
        if seals:
            ck.eq(jsha(note), m["input_seals"]["original_note_seals"][note["id"]],
                  "reviewed.original-seal:" + note["id"])
    ev = m["later_source_clarification_evidence"]
    ck.eq(ev["lines"], [454, 459], "notes.degree-source-lines")
    ck.eq(ev["sha256"], sha(context["later"]), "notes.degree-source-hash")
    ck.eq(ev["git_blob_sha1"], blob(context["later"]), "notes.degree-source-blob")
    ck.eq(ev["bytes"], len(context["later"]), "notes.degree-source-bytes")
    excerpt = "".join(context["later"].decode().splitlines(keepends=True)[453:459])
    ck.eq(ev["raw_excerpt"], excerpt, "notes.degree-source-excerpt")
    ck.eq(ev["excerpt_sha256"], sha(excerpt), "notes.degree-excerpt-hash")
    ck.eq(t["original_notes"][1]["source_evidence"], ev, "notes.degree-evidence")
    ck.eq(m["canon_receipts"], context["canon_paths"], "canon.three-stages")
    ck.eq([read_json(LOCALE / p)["stage"] for p in m["canon_receipts"]],
          ["draft", "revision", "qa"], "canon.stage-order")
    for path in m["canon_receipts"]:
        receipt = read_json(LOCALE / path)
        ck.yes(bool(receipt.get("actual_decisions") or receipt.get("actual_checks")
                    or receipt.get("decisions") or receipt.get("applications")
                    or all(e.get("application") for e in receipt["examples"])), "canon.logged-decisions")
        for entry in receipt["examples"]:
            raw = (ROOT / entry["path"]).read_bytes()
            ck.eq(sha(raw), entry["text_raw_sha256"], "canon.file")
            line = raw.decode("utf-8").splitlines()[entry["line"] - 1]
            ck.eq(sha(line), entry["paragraph_sha256"], "canon.paragraph")
    if seals:
        ck.eq(jsha(t["provisional_terms"]), m["input_seals"]["terms_seal"], "reviewed.terms-seal")
        ck.eq(jsha(t["original_accessibility_alts"]), m["input_seals"]["original_accessibility_seal"],
              "reviewed.alt-seal")
        ck.eq(sha(WITNESS.read_bytes()), m["input_seals"]["source_excerpt_sha256"], "reviewed.witness-seal")
    return ck.count


def mutations(m, t, w, context):
    result = []
    def test(name, change, prefix, sealed=False):
        mm, tt, ww = copy.deepcopy(m), copy.deepcopy(t), copy.deepcopy(w)
        change(mm, tt, ww)
        try:
            validate(mm, tt, ww, context, seals=sealed)
        except Failure as exc:
            if not str(exc).startswith(prefix):
                raise Failure(f"mutation {name} wrong rejection: {exc}; expected {prefix}")
            result.append({"name": name, "rejected_by": str(exc),
                           "reviewed_seal_required": sealed})
        else:
            raise Failure("MUTATION ACCEPTED: " + name)
    def block(mm, key):
        return next(b for b in mm["source_blocks"] if b["key"] == key)
    k = SY + "#table/1/row/5/cell/1"
    test("source-variable", lambda mm,tt,ww: block(mm,k).__setitem__("source_raw", r"\( x_{i,j} \)"), "source.raw")
    test("source-index", lambda mm,tt,ww: block(mm,k)["slots"][0].__setitem__("value", " h_{j,i} "), "source.exact-slots")
    test("source-brace", lambda mm,tt,ww: block(mm,k)["slots"][0].__setitem__("raw", r"\( h_i,j} \)"), "source.exact-slots")
    test("source-slot-owner", lambda mm,tt,ww: block(mm,k)["slots"][0].__setitem__("file_start", 0), "source.exact-slots")
    test("source-table-cell-omission", lambda mm,tt,ww: mm["source_blocks"].pop(10), "scope.manifest-keys-order")
    test("source-table-cell-duplicate", lambda mm,tt,ww: mm["source_blocks"].insert(10,copy.deepcopy(mm["source_blocks"][10])), "scope.manifest-keys-order")
    test("source-table-regrouping", lambda mm,tt,ww: block(mm,k).__setitem__("column", 2), "source.span.column")
    test("source-table-order", lambda mm,tt,ww: mm["source_blocks"].__setitem__(slice(10,12),list(reversed(mm["source_blocks"][10:12]))), "scope.manifest-keys-order")
    test("source-table-shape", lambda mm,tt,ww: mm["table_layouts"][0].__setitem__("rows", 19), "table.layouts")
    test("source-id-comparison-displacement", lambda mm,tt,ww: block(mm,k)["comparison"].__setitem__("start",0), "source.comparison-span")
    test("source-witness-whitespace", lambda mm,tt,ww: ww["files"][3].__setitem__("text",ww["files"][3]["text"].replace("This book","This  book",1)), "witness.exact-text")
    test("source-witness-comment-erasure", lambda mm,tt,ww: ww["files"][3].__setitem__("text",active(ww["files"][3]["text"])), "witness.exact-text")
    test("source-comment-paragraph-break", lambda mm,tt,ww: block(mm,PF+"#paragraph/5").__setitem__("active_tex",block(mm,PF+"#paragraph/5")["active_tex"].replace("While","\nWhile",1)), "source.active-comments")
    multi = SY + "#table/1/row/1/cell/1"
    test("target-slot-order", lambda mm,tt,ww: tt["source_blocks"].__setitem__(multi,"{{tex:1}}, {{tex:0}}, {{tex:2}}"), "target.slot-order")
    test("target-slot-omission", lambda mm,tt,ww: tt["source_blocks"].__setitem__(multi,"{{tex:0}}, {{tex:1}}"), "target.slot-order")
    test("target-pure-math-arabic-comma", lambda mm,tt,ww: tt["source_blocks"].__setitem__(multi,"{{tex:0}}، {{tex:1}}، {{tex:2}}"), "target.pure-math-cell")
    test("target-week-numeral", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#table/1/row/2/cell/1",'<bdi dir="ltr">9</bdi>'), "target.week")
    refkey = PF + "#table/1/row/3/cell/2"
    test("target-week-section-ref", lambda mm,tt,ww: tt["source_blocks"].__setitem__(refkey,tt["source_blocks"][refkey].replace("One.III","One.II")), "target.section-references")
    test("target-range-minus", lambda mm,tt,ww: tt["source_blocks"].__setitem__(refkey,tt["source_blocks"][refkey].replace("–","−")), "target.section-references")
    classkey = PF + "#table/1/row/7/cell/2"
    test("target-classday-em-dash", lambda mm,tt,ww: tt["source_blocks"].__setitem__(classkey,tt["source_blocks"][classkey].replace("–","—")), "target.classday")
    test("target-publication-date", lambda mm,tt,ww: tt["source_blocks"].__setitem__("src/publicationdate.tex#date",'<bdi dir="ltr" lang="en">2026-Aug-31</bdi>'), "target.credit")
    test("target-source-credit-name", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#table/2/row/4/cell/1",'<em>–<bdi dir="ltr" lang="en">James Joyce</bdi></em>'), "target.credit")
    test("target-credit-zip", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#table/4/row/4/cell/1",'<bdi dir="ltr" lang="en">Colchester, Vermont USA 05438</bdi>'), "target.credit")
    test("target-invented-linebreak", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#table/3/row/2/cell/1",tt["source_blocks"][PF+"#table/3/row/2/cell/1"]+"\n"), "target.no-invented-linebreak")
    test("target-quote-line-omission", lambda mm,tt,ww: tt["source_blocks"].pop(PF+"#table/3/row/2/cell/1"), "scope.target-keys-order")
    test("target-isolation-rtl", lambda mm,tt,ww: tt["source_blocks"].__setitem__(refkey,tt["source_blocks"][refkey].replace('dir="ltr"','dir="rtl"')), "html.bdi-attrs")
    test("target-hidden-injection", lambda mm,tt,ww: tt["source_blocks"].__setitem__(k,'<span style="display:none">999</span>{{tex:0}}'), "html.span-attrs")
    test("target-mathml-injection", lambda mm,tt,ww: tt["source_blocks"].__setitem__(k,'<math><mn>999</mn></math>{{tex:0}}'), "html.tag")
    guide = SY + "#table/2/row/2/cell/2"
    test("target-Indonesian-pronunciation", lambda mm,tt,ww: tt["source_blocks"].__setitem__(guide,tt["source_blocks"][guide].replace("AL-fuh","AL-fa")), "target.guide-source")
    test("target-visible-pronunciation-erasure", lambda mm,tt,ww: tt["source_blocks"].__setitem__(guide,tt["source_blocks"][guide].replace('>AL-fuh</bdi>','>AL-fa</bdi>')), "target.guide-words")
    test("target-emphasis-erasure", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#paragraph/7",tt["source_blocks"][PF+"#paragraph/7"].replace("<em>","").replace("</em>","")), "target.emphasis")
    test("asset-hash", lambda mm,tt,ww: tt["original_accessibility_alts"][0].__setitem__("source_sha256","0"*64), "asset.alt-sha")
    test("asset-invented-source-alt", lambda mm,tt,ww: tt["original_accessibility_alts"][0].__setitem__("source_alt","three planes"), "asset.no-fabricated-source-alt")
    test("asset-origin-laundering", lambda mm,tt,ww: tt["original_accessibility_alts"][0].__setitem__("origin","canonical-source"), "asset.original-alt")
    test("note-injected-source-key", lambda mm,tt,ww: tt["source_blocks"].__setitem__("b40-opening-degree-qualification","invented source"), "scope.target-keys-order")
    test("note-origin-laundering", lambda mm,tt,ww: tt["original_notes"][1].__setitem__("kind","source-translation"), "notes.origin")
    test("note-evidence-altered", lambda mm,tt,ww: tt["original_notes"][1]["source_evidence"].__setitem__("raw_excerpt","all polynomials"), "notes.degree-evidence")
    test("scope-false-frontmatter-complete", lambda mm,tt,ww: tt.__setitem__("whole_frontmatter_complete",True), "scope.translation")
    test("notice-wrong-license", lambda mm,tt,ww: mm["retained_notices"].__setitem__("selected_license","CC-BY-NC-SA-4.0"), "notice.distinct-license")
    test("scope-skip-required-TOC", lambda mm,tt,ww: mm["boundary"]["first_outside"].__setitem__("line",55), "scope.outside-line")
    # The following are reviewed-language change detectors, not automated semantic proof.
    test("reviewed-preface-prose-injection", lambda mm,tt,ww: tt["source_blocks"].__setitem__(PF+"#paragraph/1",tt["source_blocks"][PF+"#paragraph/1"]+" ایہہ سارا کم مک گیا اے۔"), "reviewed.target-seal", True)
    test("reviewed-original-note-overreach", lambda mm,tt,ww: tt["original_notes"][1].__setitem__("html","<p>اصل کثیرحدیاں دا درجہ ضرور برابر ہُندا اے۔</p>"), "reviewed.original-seal", True)
    return result


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    m, t, w = read_json(MANIFEST), read_json(TRANSLATION), read_json(WITNESS)
    context = build_context(m)
    context.update(frozen_source_files=copy.deepcopy(m["source_files"]),
                   frozen_comparison={b["key"]:copy.deepcopy(b["comparison"]) for b in m["source_blocks"]},
                   plan=read_json(LOCALE / m["source_plan"]),
                   canon_paths=["canon/receipts/B40-opening-draft-20260831T162851824Z.json",
                                "canon/receipts/B40-opening-revision-20260831T163947716Z.json",
                                "canon/receipts/B40-opening-qa-20260831T164611989Z.json"])
    count = context["pin_checks"] + validate(m, t, w, context)
    tests = mutations(m, t, w, context)
    paths = [MANIFEST, TRANSLATION, WITNESS, Path(__file__).resolve(),
             LOCALE / "qa/b40-opening-language-notes.md", LOCALE / m["source_plan"]]
    receipt = {
        "schema":"pnb-b40-opening-source-bound-input-qa-v1", "unit":"B40-opening",
        "status":"passed input-only checkpoint", "checks":count, "detached_mutation_count":len(tests),
        "counts":m["counts"], "source_pins":{"canonical":EN_PIN,"comparison":ID_PIN},
        "input_hashes":{p.relative_to(LOCALE).as_posix():sha(p.read_bytes()) for p in paths},
        "canon_receipts":{p:sha((LOCALE/p).read_bytes()) for p in m["canon_receipts"]},
        "source_coverage":{
            "independent_span_discovery":"174 exact canonical spans; six brace-aware active tabular layouts; all20 complete preface paragraphs including comments; source order and 138 cells",
            "raw_file_witnesses":12, "exact_tex_slots":76, "exact_other_slots":6,
            "pdf_components":"two unchanged originals bound by SHA256, Git blob and byte count; original accessibility descriptions are not source alts",
            "first_outside":m["boundary"]["first_outside"]},
        "detached_mutations":tests,
        "limits":[
            "No reader, derived MathML, upstream engine, external service or runtime executed. This is not browser/assistive-technology QA.",
            "Source spans/table/slot/credit/pronunciation checks are independently rederived; Punjabi text seals only detect edits after actual source/canon review, not semantic or native-speaker certification.",
            "Indonesian full raw witnesses and exact174 comparison spans remain inspectable; comparison-owner seals prevent reassignment, but are not a second independent Indonesian segmenter.",
            "PDF visual inspection and source-specific original alts are human/agent inspection records, not inferred from file hashes; no image or license modified.",
            "Macro dependencies are pinned and inert; future finite MathML parser and independently derived expected trees remain required.",
            "Generated contents and starred-subsection explanation remain required before main matter. Neither whole frontmatter, book nor five-work assignment is complete."
        ],
        "whole_frontmatter_complete":False, "whole_book_translation_complete":False,
        "whole_assignment_complete":False}
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status":"passed", "checks":count, "detached_mutations":len(tests),
                      "receipt_sha256":sha(RECEIPT.read_bytes())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
