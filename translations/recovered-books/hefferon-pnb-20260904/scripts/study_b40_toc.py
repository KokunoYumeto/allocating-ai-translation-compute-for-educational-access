"""Read-only, fail-closed study of B40's generated table of contents.

This is deliberately not a TeX implementation.  It reads only the pinned
``book.tex`` include list and a finite set of reviewed heading commands.  It
does not execute TeX, Asymptote, Sage, repository scripts, or network code.

The report proves the source-owned hierarchy that *would* feed
``\\tableofcontents``.  It also checks the frozen official PDF comparison and
explains why that older generated artifact cannot supply page numbers for the
current pinned source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


REPO = Path(__file__).resolve().parents[3]
CANON = REPO / "downloads/upstream/hefferon-linear-algebra"
ID = REPO / "downloads/hefferon-linear-algebra-id"
CANON_SRC = CANON / "src"
ID_SRC = ID / "source/linear-algebra/src"
AUTHORITY_PDF = ID / "authority/official/book.pdf"

EXPECTED_INCLUDES = [
    "gr/gr1", "gr/gr2", "gr/gr3", "gr/cas", "gr/leontief",
    "gr/ppivot", "gr/network", "vs/vs1", "vs/vs2", "vs/vs3",
    "vs/fields", "vs/crystal", "vs/voting", "vs/dimen", "map/map1",
    "map/map2", "map/map3", "map/map4", "map/map5", "map/map6",
    "map/lstsqs", "map/homogeom", "map/magicsqs", "map/markov",
    "map/erlang", "det/det1", "det/det2", "det/det3", "det/cramer",
    "det/detspeed", "det/chio", "det/projplane", "det/compgraphics",
    "jc/jc1", "jc/jc2", "jc/jc3", "jc/jc4", "jc/powers", "jc/pops",
    "jc/search", "jc/recur", "jc/wilber", "jc/innerproduct",
    "appen/appen", "bib/bib",
]

EXPECTED = {
    "canonical_commit": "df2262e089a02651c127f1dd12649c4622ee1383",
    "canonical_tree": "94255d684882ac8422e97640254c84347e2d1690",
    "comparison_commit": "e84ce2956a7304830c42eba70106f940fefee7c4",
    "comparison_tree": "b434745225bb3931d51d107d8d8e5c0c8707af5d",
    "canonical_book_logical_lf_sha256":
        "5493db2d10853ad7fdce70b4e6cc65174b7dbb3a66d8d654782977e7137abaaa",
    "comparison_book_logical_lf_sha256":
        "a260d6dc1036c61644cc8ae3522b17924a943dd3d8f7209576b7bc8e72b95b8b",
    "canonical_style_logical_lf_sha256":
        "3d5f6f14a0b433089fc25b9b88ab481434bd6266e09f84292477e96c2c6160f6",
    "authority_pdf_sha256":
        "5240f2782e645bc6351ad9eba69d8c19500142a5cca9c90450c17b3765a1a400",
    "authority_pdf_bytes": 7_626_685,
    "authority_pdf_pages": 525,
}

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}
ENGLISH = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
COMMANDS = ("chapter", "section", "subsection", "subsectionoptional", "topic",
            "appendsection")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def logical_lf(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n")


def read_lf(path: Path) -> str:
    return logical_lf(path.read_bytes()).decode("utf-8")


def is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and text[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def strip_comments_preserve(text: str) -> str:
    """Blank active TeX comments while retaining byte-position line mapping."""
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == "%" and not is_escaped(text, i):
            while i < len(chars) and chars[i] != "\n":
                chars[i] = " "
                i += 1
        else:
            i += 1
    return "".join(chars)


def active_text(text: str) -> str:
    """Return comment-stripped text truncated after the first active endinput.

    LaTeX's primitive ``\\endinput`` discards the remainder of the current
    input file.  Several source files retain dead material after it, so merely
    scanning balanced commands would invent TOC entries.
    """
    active = strip_comments_preserve(text)
    match = re.search(r"\\endinput\b", active)
    if match:
        active = active[:match.start()] + " " * (len(active) - match.start())
    return active


def read_group(text: str, open_index: int) -> tuple[str, int]:
    if open_index >= len(text) or text[open_index] != "{":
        raise ValueError(f"Expected group at codepoint {open_index}")
    depth = 1
    i = open_index + 1
    while i < len(text):
        if text[i] == "{" and not is_escaped(text, i):
            depth += 1
        elif text[i] == "}" and not is_escaped(text, i):
            depth -= 1
            if depth == 0:
                return text[open_index + 1:i], i + 1
        i += 1
    raise ValueError(f"Unclosed group at codepoint {open_index}")


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


@dataclass(frozen=True)
class Command:
    kind: str
    starred: bool
    argument: str
    line: int
    occurrence: int


def commands(path: Path) -> list[Command]:
    original = read_lf(path)
    active = active_text(original)
    pattern = re.compile(r"\\(" + "|".join(COMMANDS) + r")(\*)?\s*\{")
    counts: dict[str, int] = {}
    found: list[Command] = []
    for match in pattern.finditer(active):
        argument, _ = read_group(active, match.end() - 1)
        kind = match.group(1)
        counts[kind] = counts.get(kind, 0) + 1
        found.append(Command(kind, bool(match.group(2)), argument,
                             line_number(original, match.start()), counts[kind]))
    return found


def invocation_coverage(path: Path) -> dict:
    """Prove every active reviewed heading token uses the accepted form."""
    original = read_lf(path)
    active = active_text(original)
    token = re.compile(r"\\(" + "|".join(COMMANDS) + r")\b\*?\s*(?=\[|\{)")
    tokens = list(token.finditer(active))
    parsed = commands(path)
    optional_argument_forms = [
        {"kind": m.group(1), "line": line_number(original, m.start())}
        for m in tokens if active[m.end():].lstrip().startswith("[")
    ]
    if optional_argument_forms:
        raise AssertionError(f"Unsupported optional heading arguments in {path}: {optional_argument_forms}")
    if len(tokens) != len(parsed):
        raise AssertionError(f"Uncovered heading invocation in {path}: {len(tokens)} != {len(parsed)}")
    return {"path": path.relative_to(REPO).as_posix(), "invocations": len(parsed)}


def dead_headings(path: Path) -> list[dict]:
    """List command-shaped source retained after an active endinput."""
    original = read_lf(path)
    stripped = strip_comments_preserve(original)
    stop = re.search(r"\\endinput\b", stripped)
    if not stop:
        return []
    tail = stripped[stop.end():]
    pattern = re.compile(r"\\(" + "|".join(COMMANDS) + r")(\*)?\s*\{")
    out = []
    for match in pattern.finditer(tail):
        argument, _ = read_group(tail, match.end() - 1)
        absolute = stop.end() + match.start()
        out.append({
            "path": path.relative_to(REPO).as_posix(),
            "line": line_number(original, absolute),
            "kind": match.group(1),
            "raw_title": argument,
            "reason_inert": f"active \\endinput at line {line_number(original, stop.start())}",
        })
    return out


def active_include_order(src: Path) -> list[str]:
    text = active_text(read_lf(src / "book.tex"))
    main_start = text.index("\\mainmatter")
    end = text.index("\\printindex", main_start)
    scope = text[main_start:end]
    out = []
    for match in re.finditer(r"\\include\s*\{", scope):
        value, _ = read_group(scope, match.end() - 1)
        out.append(value)
    if out != EXPECTED_INCLUDES:
        raise AssertionError(f"Unexpected active main include order: {out!r}")
    return out


def appendix_entries(path: Path, comparison: bool) -> list[dict]:
    original = read_lf(path)
    active = active_text(original)
    chapter = next(c for c in commands(path) if c.kind == "chapter" and c.starred)
    expected_chapter = "Lampiran" if comparison else "Appendix"
    if chapter.argument != expected_chapter:
        raise AssertionError((path, chapter.argument))
    literal = r"\\addcontentsline{toc}{chapter}{" + re.escape(expected_chapter) + r"}"
    m = re.search(literal, active)
    if not m:
        raise AssertionError(f"Missing explicit appendix chapter TOC owner in {path}")
    entries = [{
        "owner": f"src/appen/appen.tex#addcontentsline/chapter/1",
        "file": "src/appen/appen.tex",
        "line": line_number(original, m.start()),
        "kind": "chapter",
        "generated_label": None,
        "raw_title": expected_chapter,
        "optional_star": False,
        "page_number_source": None,
    }]
    for c in commands(path):
        if c.kind == "appendsection":
            entries.append({
                "owner": f"src/appen/appen.tex#appendsection/{c.occurrence}",
                "file": "src/appen/appen.tex",
                "line": c.line,
                "kind": "appendix-subsection",
                "generated_label": None,
                "raw_title": c.argument,
                "optional_star": False,
                "page_number_source": "generated-only",
            })
    if len(entries) != 5:
        raise AssertionError(f"Expected appendix plus four entries, got {len(entries)}")
    return entries


def build_entries(src: Path, comparison: bool = False) -> list[dict]:
    includes = active_include_order(src)
    entries: list[dict] = []
    chapter_number = 0
    section_number = 0
    subsection_number = 0
    per_file: dict[tuple[str, str], int] = {}
    for include in includes:
        rel = f"src/{include}.tex"
        path = src / f"{include}.tex"
        if include == "appen/appen":
            entries.extend(appendix_entries(path, comparison))
            continue
        if include == "bib/bib":
            if any(c.kind in COMMANDS for c in commands(path)):
                raise AssertionError("Bibliography unexpectedly has explicit heading commands")
            continue
        for c in commands(path):
            key = (rel, c.kind)
            per_file[key] = per_file.get(key, 0) + 1
            owner = f"{rel}#{c.kind}/{per_file[key]}"
            if c.kind == "chapter":
                if c.starred:
                    raise AssertionError(f"Unexpected starred main chapter at {owner}")
                chapter_number += 1
                section_number = 0
                subsection_number = 0
                generated = f"Chapter {ENGLISH[chapter_number]}:"
                kind = "chapter"
            elif c.kind == "section":
                if c.starred:
                    raise AssertionError(f"Unexpected starred numbered section at {owner}")
                section_number += 1
                subsection_number = 0
                generated = ROMAN[section_number]
                kind = "section"
            elif c.kind in {"subsection", "subsectionoptional"}:
                if c.starred:
                    raise AssertionError(f"Unexpected command-star subsection at {owner}")
                subsection_number += 1
                generated = f"{ROMAN[section_number]}.{subsection_number}"
                kind = "subsection"
            elif c.kind == "topic":
                if c.starred:
                    raise AssertionError(f"Unexpected starred topic at {owner}")
                section_number += 1  # exact source macro side effect
                subsection_number = 0
                generated = "Topic:"
                kind = "topic"
            else:
                raise AssertionError(c)
            entries.append({
                "owner": owner,
                "file": rel,
                "line": c.line,
                "kind": kind,
                "generated_label": generated,
                "raw_title": c.argument,
                "optional_star": c.kind == "subsectionoptional",
                "page_number_source": None if kind == "chapter" else "generated-only",
            })
    if chapter_number != 5:
        raise AssertionError(f"Expected five numbered chapters, got {chapter_number}")
    return entries


def structure(entry: dict) -> tuple:
    return (entry["owner"], entry["kind"], entry["generated_label"],
            entry["optional_star"], entry["page_number_source"])


def compact_digest(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
    return sha256(data)


def file_record(path: Path, role: str) -> dict:
    raw = path.read_bytes()
    return {
        "role": role,
        "path": path.relative_to(REPO).as_posix(),
        "bytes": len(raw),
        "raw_sha256": sha256(raw),
        "logical_lf_sha256": sha256(logical_lf(raw)),
    }


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    command = ["git", "-C", str(repo), *args]
    if input_bytes is None:
        return subprocess.check_output(command, stdin=subprocess.DEVNULL)
    return subprocess.check_output(command, input=input_bytes)


def batch_blobs(repo: Path, commit: str, paths: list[str]) -> dict[str, tuple[str, bytes]]:
    requests = "".join(f"{commit}:{path}\n" for path in paths).encode()
    output = git(repo, "cat-file", "--batch", input_bytes=requests)
    result: dict[str, tuple[str, bytes]] = {}
    cursor = 0
    for path in paths:
        line_end = output.index(b"\n", cursor)
        header = output[cursor:line_end].decode("ascii")
        cursor = line_end + 1
        parts = header.split()
        if len(parts) != 3 or parts[1] != "blob":
            raise AssertionError(f"Unexpected Git object for {path}: {header}")
        blob_sha1, _, size_raw = parts
        size = int(size_raw)
        data = output[cursor:cursor + size]
        cursor += size
        if output[cursor:cursor + 1] != b"\n":
            raise AssertionError(f"Missing Git batch delimiter after {path}")
        cursor += 1
        result[path] = (blob_sha1, data)
    if cursor != len(output):
        raise AssertionError("Unparsed Git batch output")
    return result


def repository_records(repo: Path, src_prefix: str, role: str,
                       commit: str, tree: str) -> dict:
    head = git(repo, "rev-parse", "HEAD").decode().strip()
    observed_commit = git(repo, "rev-parse", commit + "^{commit}").decode().strip()
    observed_tree = git(repo, "rev-parse", commit + "^{tree}").decode().strip()
    if head != commit or observed_commit != commit or observed_tree != tree:
        raise AssertionError(f"Pinned repository identity mismatch: {role}")
    relative = ["book.tex", "sty/bookjhconcrete.sty"] + [
        f"{include}.tex" for include in EXPECTED_INCLUDES
    ]
    relative = list(dict.fromkeys(relative))
    repository_paths = [src_prefix + path for path in relative]
    blobs = batch_blobs(repo, commit, repository_paths)
    files = []
    for local_rel, repository_path in zip(relative, repository_paths):
        blob_sha1, data = blobs[repository_path]
        working = (repo / repository_path).read_bytes()
        if logical_lf(working) != data:
            raise AssertionError(f"Working file differs from pinned blob: {role} {repository_path}")
        files.append({
            "repository_path": repository_path,
            "bytes": len(data),
            "sha256": sha256(data),
            "git_blob_sha1": blob_sha1,
            "working_raw_sha256": sha256(working),
            "working_logical_lf_sha256": sha256(logical_lf(working)),
        })
    return {
        "role": role,
        "local_path": repo.relative_to(REPO).as_posix(),
        "commit": commit,
        "tree": tree,
        "head": head,
        "selected_file_count": len(files),
        "selected_files": files,
        "selected_files_compact_sha256": compact_digest(files),
    }


def legend_record(src: Path) -> dict:
    original = read_lf(src / "book.tex")
    lines = original.splitlines()
    line = lines[50]
    active = active_text(line).rstrip()
    marker = r"${}^*\!$"
    if marker not in active:
        raise AssertionError(f"Missing exact star marker on book.tex:51: {active!r}")
    before, after = active.split(marker, 1)
    suffix = r"\clearemptydoublepage"
    if not after.endswith(suffix):
        raise AssertionError(after)
    text = after[:-len(suffix)]
    return {
        "owner": "src/book.tex#line/51/starred-subsections-explanation",
        "line": 51,
        "active_raw": active,
        "active_raw_sha256": sha256(active.encode()),
        "marker_raw_tex": marker,
        "marker_tokens": ["{", "}", "^", "*", r"\!"],
        "text": text,
        "prefix_raw": before,
        "suffix_raw": suffix,
    }


def authority_pdf_record() -> dict:
    raw = AUTHORITY_PDF.read_bytes()
    if len(raw) != EXPECTED["authority_pdf_bytes"] or sha256(raw) != EXPECTED["authority_pdf_sha256"]:
        raise AssertionError("Official authority PDF identity mismatch")
    reader = PdfReader(AUTHORITY_PDF)
    if len(reader.pages) != EXPECTED["authority_pdf_pages"]:
        raise AssertionError("Official authority PDF page count mismatch")
    blob_sha1, pinned_pdf = batch_blobs(
        ID, EXPECTED["comparison_commit"], ["authority/official/book.pdf"]
    )["authority/official/book.pdf"]
    if pinned_pdf != raw:
        raise AssertionError("Working authority PDF differs from the pinned Git blob")
    artifact_path = ID / "backend/artifacts.jsonl"
    artifact_rows = [json.loads(line) for line in artifact_path.read_text(encoding="utf-8").splitlines()
                     if line.strip()]
    artifact = [row for row in artifact_rows
                if row.get("source_locator") == "authority/official/book.pdf"]
    if len(artifact) != 1:
        raise AssertionError("Expected one existing official textbook artifact row")
    artifact = artifact[0]
    for field, value in (("sha256", EXPECTED["authority_pdf_sha256"]),
                         ("bytes", EXPECTED["authority_pdf_bytes"]),
                         ("page_count", EXPECTED["authority_pdf_pages"]),
                         ("build_status", "official authority comparison artifact")):
        if artifact.get(field) != value:
            raise AssertionError(f"Authority artifact row differs: {field}")
    contents = "\n".join((reader.pages[i].extract_text() or "") for i in range(6, 9))
    if "Topic: Coupled Oscillators" not in contents:
        raise AssertionError("Expected older authority TOC terminal topic not found")
    if "Topic: Inner Product" in contents:
        raise AssertionError("Authority PDF unexpectedly contains the 2021 Inner Product topic")
    preface = "\n".join((reader.pages[i].extract_text() or "") for i in range(2, 6))
    if "2020-Apr-26" not in preface or "In the particular" not in preface:
        raise AssertionError("Expected older preface date/Joyce lines not found")
    return {
        "path": AUTHORITY_PDF.relative_to(REPO).as_posix(),
        "bytes": len(raw),
        "sha256": sha256(raw),
        "git_blob_sha1": blob_sha1,
        "pages": len(reader.pages),
        "existing_artifact_row": artifact,
        "existing_artifact_row_sha256": compact_digest(artifact),
        "metadata_creation_date": str(reader.metadata.get("/CreationDate")),
        "visually_inspected_physical_pages": [7, 8, 9, 10],
        "toc_text_physical_pages": [7, 8, 9],
        "blank_after_toc_physical_page": 10,
        "staleness_evidence": [
            "TOC ends Chapter Five topics at Coupled Oscillators and omits current src/jc/innerproduct.tex Topic: Inner Product.",
            "Preface credit says 2020-Apr-26 while current pinned src/publicationdate.tex says 2021-Oct-12.",
            "PDF displays the James Joyce quotation that is commented out in the current pinned preface source.",
        ],
        "use": "bounded visual/generated-layout comparison only; not current page-number authority",
    }


def mutate_and_reject() -> list[str]:
    canonical_book = read_lf(CANON_SRC / "book.tex")
    cases = {
        "remove-innerproduct-include": canonical_book.replace(r"\include{jc/innerproduct}", "", 1),
        "activate-commented-eigengeom": canonical_book.replace(r"%\include{eigengeom}", r"\include{eigengeom}", 1),
        "change-star-legend": canonical_book.replace(r"${}^*\!$", r"${}^+\!$", 1),
    }
    rejected = []
    for name, mutated in cases.items():
        active = active_text(mutated)
        includes = []
        scope = active[active.index(r"\mainmatter"):active.index(r"\printindex")]
        for match in re.finditer(r"\\include\s*\{", scope):
            value, _ = read_group(scope, match.end() - 1)
            includes.append(value)
        valid = includes == EXPECTED_INCLUDES and r"${}^*\!$" in active.splitlines()[50]
        if valid:
            raise AssertionError(f"Mutation was not rejected: {name}")
        rejected.append(name)
    return rejected


def report() -> dict:
    repositories = {
        "canonical": repository_records(
            CANON, "src/", "canonical",
            EXPECTED["canonical_commit"], EXPECTED["canonical_tree"]),
        "comparison": repository_records(
            ID, "source/linear-algebra/src/", "comparison",
            EXPECTED["comparison_commit"], EXPECTED["comparison_tree"]),
    }
    canon_book = file_record(CANON_SRC / "book.tex", "canonical-root")
    id_book = file_record(ID_SRC / "book.tex", "comparison-root")
    canon_style = file_record(CANON_SRC / "sty/bookjhconcrete.sty", "canonical-toc-style")
    if canon_book["logical_lf_sha256"] != EXPECTED["canonical_book_logical_lf_sha256"]:
        raise AssertionError("Canonical book.tex logical-LF hash mismatch")
    if id_book["logical_lf_sha256"] != EXPECTED["comparison_book_logical_lf_sha256"]:
        raise AssertionError("Comparison book.tex logical-LF hash mismatch")
    if canon_style["logical_lf_sha256"] != EXPECTED["canonical_style_logical_lf_sha256"]:
        raise AssertionError("Canonical style logical-LF hash mismatch")

    canonical = build_entries(CANON_SRC)
    comparison = build_entries(ID_SRC, comparison=True)
    if [structure(x) for x in canonical] != [structure(x) for x in comparison]:
        raise AssertionError("Canonical/comparison generated-TOC structures diverge")

    kinds = {kind: sum(x["kind"] == kind for x in canonical)
             for kind in ("chapter", "section", "subsection", "topic", "appendix-subsection")}
    kinds["total"] = len(canonical)
    kinds["optional_subsections"] = sum(x["optional_star"] for x in canonical)
    kinds["entries_with_generated_page_numbers"] = sum(
        x["page_number_source"] == "generated-only" for x in canonical)
    kinds["chapter_entries_without_page_numbers_by_style"] = sum(
        x["kind"] == "chapter" and x["page_number_source"] is None for x in canonical)

    current_inner = next(x for x in canonical if x["file"] == "src/jc/innerproduct.tex")
    if current_inner["raw_title"] != "Inner Product" or current_inner["kind"] != "topic":
        raise AssertionError(current_inner)

    coverage = {"canonical": [], "comparison": []}
    inert = {"canonical": [], "comparison": []}
    manual_toc = {"canonical": [], "comparison": []}
    for label, root in (("canonical", CANON_SRC), ("comparison", ID_SRC)):
        for include in EXPECTED_INCLUDES:
            path = root / f"{include}.tex"
            coverage[label].append(invocation_coverage(path))
            inert[label].extend(dead_headings(path))
            original = read_lf(path)
            active = active_text(original)
            for match in re.finditer(r"\\addcontentsline\s*\{toc\}", active):
                manual_toc[label].append({
                    "path": path.relative_to(REPO).as_posix(),
                    "line": line_number(original, match.start()),
                })
        if len(manual_toc[label]) != 2 or not all(
                x["path"].endswith("src/appen/appen.tex") for x in manual_toc[label]):
            raise AssertionError(f"Unexpected manual TOC owners: {label} {manual_toc[label]}")
    expected_inert = {
        "canonical": ("src/gr/gr1.tex", 5065, "subsection", "Comparing Set Descriptions"),
        "comparison": ("src/gr/gr1.tex", 5033, "subsection", "Membandingkan Deskripsi Himpunan"),
    }
    for label, expected in expected_inert.items():
        selected = [x for x in inert[label] if x["path"].endswith(expected[0])]
        if len(selected) != 1 or (selected[0]["line"], selected[0]["kind"],
                                  selected[0]["raw_title"]) != expected[1:]:
            raise AssertionError(f"Unexpected gr1 endinput result: {label} {selected}")

    return {
        "schema": "pnb-b40-generated-toc-source-study-v1",
        "unit_proposal": "B40-toc",
        "status": "source study only; production blocked on current generated page-number authority",
        "runtime": "read-only pinned byte parsing plus pypdf extraction; no TeX, Asymptote, Sage, upstream code, network, analytics or grading runtime",
        "repositories": repositories,
        "inputs": [canon_book, id_book, canon_style],
        "include_order": EXPECTED_INCLUDES,
        "include_order_sha256": compact_digest(EXPECTED_INCLUDES),
        "counts": kinds,
        "canonical_entries": canonical,
        "comparison_entries": comparison,
        "canonical_entries_sha256": compact_digest(canonical),
        "comparison_entries_sha256": compact_digest(comparison),
        "canonical_structure_sha256": compact_digest([structure(x) for x in canonical]),
        "comparison_structure_sha256": compact_digest([structure(x) for x in comparison]),
        "legend": {
            "canonical": legend_record(CANON_SRC),
            "comparison": legend_record(ID_SRC),
        },
        "toc_generation_style": {
            "source": "src/sty/bookjhconcrete.sty:420-447,488-506,654-656,765-808,823-824,833-850",
            "tocdepth": 2,
            "secnumdepth": 2,
            "chapter_page_numbers": "off by \\cftpagenumbersoff{chapter}",
            "section_and_subsection_page_numbers": "generated from actual typeset pages; not source literals",
            "optional_star": "subsectionoptional writes a raised literal asterisk into the TOC title",
            "topic": "unnumbered displayed label Topic:, but source macro increments the section counter",
            "appendix": "manual chapter and four unnumbered subsection entries; pages use A-n only after typesetting",
            "bibliography": "no explicit TOC entry in this selected source/style path",
        },
        "parser_coverage": {
            "reviewed_active_heading_invocations": coverage,
            "manual_addcontentsline_owners": manual_toc,
            "inert_headings_after_endinput": inert,
            "important_correction": "src/gr/gr1.tex:5065 Comparing Set Descriptions is after active \\endinput at line5060 (comparison lines5033/5028), so it is not a generated TOC entry. Earlier boundary planning that listed it as active is superseded for TOC reconstruction.",
        },
        "authority_pdf": authority_pdf_record(),
        "blocking_finding": {
            "reason": "The exact 91 section/subsection/topic/appendix-subsection page-number strings are generated by pagination, not present in pinned TeX. The only frozen official PDF is an older generated artifact and demonstrably omits the current 2021 Inner Product topic, uses the older 2020 author date, and includes now-commented content.",
            "safe_result": "All current source-owned titles, hierarchy, numbering labels, optional-star flags and the literal legend are statically reconstructible. Current page numbers and line wrapping are not.",
            "decision": "Do not invent, copy stale page numbers, or execute the untrusted upstream TeX stack. Stop at source study until an exact generated artifact for df2262e/current files or explicit authority to publish a page-number-free semantic TOC is supplied.",
        },
        "rejected_mutations": mutate_and_reject(),
        "whole_frontmatter_complete": False,
        "whole_book_translation_complete": False,
        "whole_assignment_complete": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    result = report()
    if args.summary:
        result = {
            "status": result["status"],
            "counts": result["counts"],
            "include_order_sha256": result["include_order_sha256"],
            "canonical_entries_sha256": result["canonical_entries_sha256"],
            "comparison_entries_sha256": result["comparison_entries_sha256"],
            "canonical_structure_sha256": result["canonical_structure_sha256"],
            "comparison_structure_sha256": result["comparison_structure_sha256"],
            "canonical_legend": result["legend"]["canonical"],
            "comparison_legend": result["legend"]["comparison"],
            "authority_pdf": result["authority_pdf"],
            "blocking_finding": result["blocking_finding"],
            "parser_coverage": {
                "manual_addcontentsline_owners": result["parser_coverage"]["manual_addcontentsline_owners"],
                "inert_headings_after_endinput": result["parser_coverage"]["inert_headings_after_endinput"],
                "important_correction": result["parser_coverage"]["important_correction"],
            },
            "rejected_mutations": result["rejected_mutations"],
        }
    print(json.dumps(result, ensure_ascii=False,
                     indent=None if args.compact else 2,
                     separators=(",", ":") if args.compact else None))


if __name__ == "__main__":
    main()
