#!/usr/bin/env python3
"""Build the self-contained, offline HTML reader for the research paper.

The builder intentionally has no network or third-party runtime dependency.  It
uses PAPER.md as the prose authority and links (rather than copying) the
machine-readable evidence files in ``structured`` and ``qa``.  It is safe to
rerun after DOCX/PDF creation; files that exist at build time are offered as
download links and their byte identities are recorded in the build report.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_href(path: Path, root: Path, base: Path) -> str:
    """Return a safe, POSIX relative href for a path inside root."""
    path = path.resolve()
    root = root.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:  # pragma: no cover - defensive boundary
        raise ValueError(f"refusing path outside artifact root: {path}") from exc
    return Path(__import__("os").path.relpath(path, base.resolve())).as_posix()


def slugify(value: str, used: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "section"
    candidate = slug
    n = 2
    while candidate in used:
        candidate = f"{slug}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def split_table_row(line: str) -> list[str]:
    """Split a pipe table row while respecting escaped pipes and code spans."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells: list[str] = []
    buf: list[str] = []
    escaped = False
    code = False
    for ch in s:
        if ch == "`":
            code = not code
        if ch == "|" and not escaped and not code:
            cells.append("".join(buf).strip())
            buf = []
            continue
        if ch == "\\" and not escaped:
            escaped = True
            buf.append(ch)
            continue
        escaped = False
        buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def inline_markup(text: str) -> str:
    """Small, deliberately conservative Markdown inline renderer."""
    # Keep code spans out of subsequent substitutions.
    placeholders: list[str] = []

    def stash(m: re.Match[str]) -> str:
        placeholders.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        return f"\x00CODE{len(placeholders)-1}\x00"

    text = re.sub(r"`([^`\n]+)`", stash, text)
    text = html.escape(text, quote=False)

    # Display/inline TeX is represented as readable text, not an external
    # MathJax dependency.  Preserve the delimiters in an aria-labelled span.
    text = re.sub(
        r"\\\((.+?)\\\)",
        lambda m: '<span class="math-inline" aria-label="Mathematical expression">'
        + m.group(1)
        + "</span>",
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = text.replace("  ", "<br>\n")

    for i, value in enumerate(placeholders):
        text = text.replace(f"\x00CODE{i}\x00", value)
    return text


def render_markdown(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Render the paper's constrained Markdown subset and collect headings."""
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    headings: list[tuple[int, str, str]] = []
    used_ids: set[str] = set()
    i = 0
    paragraph: list[str] = []
    list_items: list[tuple[str, str]] = []
    list_kind: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append("<p>" + inline_markup(" ".join(x.strip() for x in paragraph)) + "</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, list_kind
        if not list_items:
            return
        tag = "ol" if list_kind == "ol" else "ul"
        out.append(f"<{tag}>")
        for _marker, value in list_items:
            out.append("<li>" + inline_markup(value) + "</li>")
        out.append(f"</{tag}>")
        list_items = []
        list_kind = None

    def flush_blocks() -> None:
        flush_paragraph()
        flush_list()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code blocks.
        if stripped.startswith("```"):
            flush_blocks()
            lang = html.escape(stripped[3:].strip(), quote=True)
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(code_lines), quote=False) + "</code></pre>")
            continue

        # Display math blocks.  This is intentionally text-first and works
        # without JavaScript or a remote renderer.
        if stripped in {"\\[", "$$"}:
            flush_blocks()
            opener = stripped
            i += 1
            math_lines: list[str] = []
            while i < len(lines) and lines[i].strip() not in ({"\\]", "$$"} if opener == "\\[" else {"$$"}):
                math_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            raw = "\n".join(math_lines)
            label = html.escape("Mathematical expression: " + re.sub(r"\s+", " ", raw).strip(), quote=True)
            out.append(f'<div class="math-block" role="img" aria-label="{label}"><code>{html.escape(raw, quote=False)}</code></div>')
            continue

        # ATX headings.
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            flush_blocks()
            level = len(m.group(1))
            title = m.group(2).strip()
            ident = slugify(title, used_ids)
            headings.append((level, title, ident))
            out.append(f'<h{level} id="{ident}">{inline_markup(title)}</h{level}>')
            i += 1
            continue

        # Pipe table (header + separator + body).
        if i + 1 < len(lines) and stripped.startswith("|") and is_table_separator(lines[i + 1]):
            flush_blocks()
            headers = split_table_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip():
                rows.append(split_table_row(lines[i]))
                i += 1
            # A caption is required for a useful screen-reader table.  The
            # nearest preceding heading gives a stable, source-derived label
            # without inventing a claim about the table's contents.
            caption = headings[-1][1] if headings else "Manuscript data table"
            out.append('<div class="table-wrap"><table><caption>' + inline_markup(caption) + '</caption>')
            out.append("<thead><tr>" + "".join(f"<th scope=\"col\">{inline_markup(c)}</th>" for c in headers) + "</tr></thead>")
            out.append("<tbody>")
            for row in rows:
                row = row + [""] * max(0, len(headers) - len(row))
                out.append("<tr>" + "".join(f"<td>{inline_markup(c)}</td>" for c in row[: len(headers)]) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        # Blockquotes, preserving paragraph boundaries inside the quote.
        if stripped.startswith(">"):
            flush_blocks()
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote><p>" + inline_markup(" ".join(quote_lines).strip()) + "</p></blockquote>")
            continue

        # Ordered/unordered lists.  Nested lists are flattened in the reader,
        # while retaining the source text and list semantics.
        lm = re.match(r"^\s*([-+*]|\d+[.)])\s+(.+)$", line)
        if lm:
            flush_paragraph()
            kind = "ol" if lm.group(1)[0].isdigit() else "ul"
            if list_kind and kind != list_kind:
                flush_list()
            list_kind = kind
            list_items.append((lm.group(1), lm.group(2).strip()))
            i += 1
            continue

        if re.fullmatch(r"\s*([-*_])(?:\s*\1){2,}\s*", line):
            flush_blocks()
            out.append("<hr>")
            i += 1
            continue

        if not stripped:
            flush_blocks()
            i += 1
            continue

        # Ignore raw HTML comments but preserve ordinary text.
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            i += 1
            continue
        paragraph.append(line)
        i += 1

    flush_blocks()
    return "\n".join(out), headings


def display_number(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"-?\d+", value):
        try:
            return f"{int(value):,}"
        except ValueError:
            pass
    if re.fullmatch(r"-?\d+\.\d+", value):
        try:
            return f"{float(value):,.6f}".rstrip("0").rstrip(".")
        except ValueError:
            pass
    return value


def csv_table(root: Path, path: Path, columns: Sequence[tuple[str, str]], caption: str, max_rows: int | None = None) -> tuple[str, int]:
    """Render a bounded CSV table and return HTML plus row count."""
    if not path.exists():
        return f'<p class="notice">Data file not present at build time: <code>{html.escape(path.name)}</code>.</p>', 0
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            if max_rows is not None and len(rows) >= max_rows:
                break
    parts = [f'<div class="table-wrap"><table><caption>{html.escape(caption)}</caption><thead><tr>']
    parts.append("".join(f'<th scope="col">{html.escape(label)}</th>' for _key, label in columns))
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        for key, _label in columns:
            val = display_number(str(row.get(key, "")))
            parts.append(f"<td>{inline_markup(val)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts), len(rows)


def artifact_links(root: Path, out_path: Path) -> tuple[str, list[dict[str, object]]]:
    """Build a compact, hash-labelled catalog of the evidence files."""
    groups: list[tuple[str, Iterable[Path]]] = [
        (
            "Rankings and decision views",
            [
                root / "structured" / n
                for n in (
                    "TOP10_NEEDS_ONLY_v3.csv",
                    "TOP100_NEEDS_ONLY_v3.csv",
                    "TOP10_COMPUTE_EFFICIENCY_v3.csv",
                    "TOP100_COMPUTE_EFFICIENCY_v3.csv",
                    "ORDER_L_M_v3.csv",
                    "ORDER_L_ID_v3.csv",
                    "ORDER_L_SENSITIVITY_v3.csv",
                    "TOP10_LANGUAGE_GROUPS_v3.csv",
                    "TOP100_LANGUAGE_GROUPS_v3.csv",
                    "TOP10_STAGE_OPPORTUNITY_v3.csv",
                    "TOP100_STAGE_OPPORTUNITY_v3.csv",
                )
            ],
        ),
        (
            "Evidence and overlap",
            [
                root / "structured" / n
                for n in (
                    "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv",
                    "GLOBAL_FUNDING_PORTFOLIO_v1.csv",
                    "GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv",
                    "SOURCE_TO_SCORE_CROSSWALK_v1.csv",
                    "RANK_SENSITIVITY_SUMMARY_v1.csv",
                    "STRUCTURAL_ACCESS_COMMISSIONING_REGISTER_v1.csv",
                    "DISPLACEMENT_EDUCATION_PORTFOLIO_v1.csv",
                    "EVIDENCE_AUTHORIZATION_v1.csv",
                    "PORTFOLIO_OVERLAP_REGISTER_v1.csv",
                    "PORTFOLIO_NONADDITIVITY_BOUNDS_v1.csv",
                    "LANGUAGE_GROUP_ORDER_L_M_v3.csv",
                    "ACCESSIBILITY_OVERLAY_ORDER_v3.csv",
                    "open_resource_canon_map.json",
                    "oer_target_canon_evidence_matrix.csv",
                )
            ],
        ),
        (
            "Stage, subject, and bridge evidence",
            [
                root / "agent_reports" / "STAGE_SUBJECT_NEEDS_MAPPING.csv",
                root / "agent_reports" / "INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv",
            ],
        ),
        (
            "QA receipts",
            [root / "qa" / n for n in (
                "GLOBAL_ACCESS_RANKINGS_V3_QA.json",
                "GLOBAL_ACCESS_RANKINGS_V3_RECEIPT.json",
                "TOP100_SOURCE_TRACE_AUDIT_v2.json",
                "PORTFOLIO_OVERLAP_AUDIT_v1.json",
                "PAPER_CITATION_AUDIT_v1.json",
                "PUBLICATION_PAPER_DATA_BINDING_AUDIT_v2.json",
                "GLOBAL_INCLUSION_DISPOSITION_QA_v1.json",
                "GLOBAL_FUNDING_PORTFOLIO_QA_v1.json",
                "RANK_SENSITIVITY_SUMMARY_QA_v1.json",
                "STRUCTURAL_ACCESS_LANES_V1_QA.json",
                "COUNTRY_TERRITORY_BINDING_AUDIT_v1.json",
                "LANGUAGE_GROUP_ORDER_V3_RECEIPT.json",
                "PAPER_DOCX_AUDIT_v1.json",
                "PAPER_PDF_AUDIT_v1.json",
                "DOCX_A11Y_AUDIT_FINAL.json",
            )],
        ),
    ]
    # Keep one identity record per relative path even though the highlighted
    # groups and the complete CSV index intentionally overlap.
    records_by_path: dict[str, dict[str, object]] = {}
    sections: list[str] = []
    for title, paths in groups:
        rows: list[str] = []
        for path in paths:
            if not path.exists():
                continue
            rel = rel_href(path, root, out_path.parent)
            digest = sha256(path)
            size = path.stat().st_size
            records_by_path[rel] = {"path": rel, "bytes": size, "sha256": digest}
            rows.append(
                f'<li><a href="{html.escape(rel, quote=True)}"><code>{html.escape(path.name)}</code></a>'
                f' <span class="file-meta">{size:,} bytes · SHA-256 <code>{digest}</code></span></li>'
            )
        if rows:
            sections.append(f"<h3>{html.escape(title)}</h3><ul class=\"file-list\">" + "".join(rows) + "</ul>")

    # Include every structured CSV as a collapsible index, so the reader is a
    # usable map even when a table is too large to embed inline.
    all_csv = sorted((root / "structured").glob("*.csv"), key=lambda p: p.name.lower())
    rows = []
    for path in all_csv:
        rel = rel_href(path, root, out_path.parent)
        digest = sha256(path)
        size = path.stat().st_size
        records_by_path[rel] = {"path": rel, "bytes": size, "sha256": digest}
        rows.append(
            f'<tr><td><a href="{html.escape(rel, quote=True)}"><code>{html.escape(path.name)}</code></a></td>'
            f'<td>{size:,}</td><td><code>{digest}</code></td></tr>'
        )
    if rows:
        sections.append(
            '<details><summary>All structured CSV files (hash-indexed)</summary>'
            '<div class="table-wrap"><table><caption>Structured evidence files available beside this reader</caption>'
            '<thead><tr><th scope="col">File</th><th scope="col">Bytes</th><th scope="col">SHA-256</th></tr></thead><tbody>'
            + "".join(rows)
            + "</tbody></table></div></details>"
        )
    records = [records_by_path[key] for key in sorted(records_by_path)]
    return "\n".join(sections), records


class _HTMLCheckParser(HTMLParser):
    """Tiny structural checker used for the durable build receipt."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.tables = 0
        self.tables_without_caption = 0
        self.tables_without_header = 0
        self._table_depth = 0
        self._table_has_caption = False
        self._table_has_header = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        d = dict(attrs)
        if "id" in d and d["id"]:
            self.ids.append(d["id"] or "")
        if tag == "a" and d.get("href"):
            self.hrefs.append(d["href"] or "")
        if tag == "table":
            self.tables += 1
            self._table_depth += 1
            self._table_has_caption = False
            self._table_has_header = False
        elif self._table_depth and tag == "caption":
            self._table_has_caption = True
        elif self._table_depth and tag in {"thead", "th"}:
            self._table_has_header = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._table_depth:
            if not self._table_has_caption:
                self.tables_without_caption += 1
            if not self._table_has_header:
                self.tables_without_header += 1
            self._table_depth -= 1


def validate_html(root: Path, output: Path) -> dict[str, object]:
    """Run bounded offline structural/link checks over the generated reader."""
    raw = output.read_text(encoding="utf-8")
    parser = _HTMLCheckParser()
    parse_error_count = 0
    try:
        parser.feed(raw)
        parser.close()
    except Exception:
        # HTMLParser is deliberately tolerant, but retain a deterministic
        # failure count if a future change introduces an invalid token stream.
        parse_error_count = 1
    missing: list[str] = []
    for href in parser.hrefs:
        parsed = urlparse(href)
        if href.startswith("#") or parsed.scheme or href.startswith("//"):
            continue
        target = (output.parent / unquote(parsed.path)).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            missing.append(href + " (outside root)")
            continue
        if not target.exists():
            missing.append(href)
    return {
        "parse_error_count": parse_error_count,
        "tag_count": len(parser.tags),
        "h1_count": sum(1 for t in parser.tags if t == "h1"),
        "heading_count": sum(1 for t in parser.tags if t in {"h1", "h2", "h3", "h4", "h5", "h6"}),
        "table_count": parser.tables,
        "tables_without_caption": parser.tables_without_caption,
        "tables_without_header": parser.tables_without_header,
        "duplicate_id_count": len(parser.ids) - len(set(parser.ids)),
        "local_link_count": sum(1 for href in parser.hrefs if not urlparse(href).scheme and not href.startswith("//") and not href.startswith("#")),
        "missing_local_links": missing,
        "external_url_count": len(re.findall(r"(?i)https?://", raw)),
        "script_tag_count": raw.lower().count("<script"),
        "required_landmarks": {name: (f"<{name}" in raw.lower()) for name in ("main", "nav", "article")},
        "skip_link_present": 'class="skip-link"' in raw,
        "offline_dependency_check": "PASS" if not re.search(r"(?i)<script|<link[^>]+href=|@import|url\(", raw) else "REVIEW",
    }


CSS = r"""
:root { color-scheme: light; --ink:#172033; --muted:#4d5b73; --line:#cbd5e1; --panel:#f5f8fc; --accent:#0b4f8a; --accent-soft:#e8f1fa; --focus:#b45309; }
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; color:var(--ink); background:#fff; font:16px/1.62 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif; }
a { color:var(--accent); text-decoration-thickness:.08em; text-underline-offset:.15em; overflow-wrap:anywhere; }
a:hover { text-decoration-thickness:.14em; }
:focus-visible { outline:3px solid var(--focus); outline-offset:3px; }
.skip-link { position:absolute; left:1rem; top:-4rem; background:#fff; color:var(--ink); padding:.65rem 1rem; border:2px solid var(--focus); z-index:10; }
.skip-link:focus { top:1rem; }
.shell { max-width:1200px; min-width:0; margin:0 auto; padding:0 1.1rem; }
.masthead { background:linear-gradient(135deg,#0b3158,#0b4f8a); color:#fff; padding:2.8rem 0 2.2rem; }
.masthead h1 { margin:.2rem 0 .65rem; max-width:35ch; font-size:clamp(2rem,5vw,3.25rem); line-height:1.1; letter-spacing:-.02em; }
.masthead p { max-width:76ch; margin:.5rem 0; color:#e7f1fb; }
.badge { display:inline-block; border:1px solid #b9d5ef; border-radius:999px; padding:.2rem .65rem; font-size:.82rem; letter-spacing:.03em; }
.layout { display:grid; grid-template-columns:minmax(0,1fr) 17rem; gap:2rem; align-items:start; min-width:0; }
main,article { min-width:0; }
nav.toc { position:sticky; top:1rem; max-height:calc(100vh - 2rem); overflow:auto; background:var(--panel); border:1px solid var(--line); border-radius:.55rem; padding:1rem; }
nav.toc h2 { font-size:1rem; margin:0 0 .5rem; }
nav.toc ol { margin:0; padding-left:1.2rem; }
nav.toc li { margin:.25rem 0; font-size:.92rem; }
nav.toc .toc-sub { list-style-type:lower-alpha; margin-top:.15rem; }
section.panel { margin:1.6rem 0; padding:1.2rem 1.35rem; border:1px solid var(--line); border-radius:.65rem; background:#fff; }
article h1, article h2, article h3, article h4 { line-height:1.25; scroll-margin-top:1rem; }
article h2 { margin-top:2.3rem; padding-bottom:.25rem; border-bottom:2px solid var(--accent-soft); }
article h3 { margin-top:1.7rem; color:#214b75; }
p { max-width:82ch; overflow-wrap:anywhere; }
blockquote { margin:1rem 0; padding:.75rem 1rem; border-left:4px solid var(--accent); background:var(--panel); }
blockquote p { margin:.1rem 0; }
code { font-family:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace; font-size:.91em; overflow-wrap:anywhere; }
pre { overflow:auto; padding:1rem; background:#101827; color:#eef5ff; border-radius:.45rem; }
.math-block { margin:1rem 0; padding:1rem; overflow:auto; background:#f8fafc; border:1px solid var(--line); border-radius:.4rem; }
.math-inline { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; background:#f5f7fa; padding:.05em .2em; border-radius:.2em; }
.table-wrap { max-width:100%; overflow-x:auto; margin:1rem 0 1.25rem; }
table { border-collapse:collapse; width:100%; min-width:34rem; font-size:.93rem; }
caption { text-align:left; font-weight:650; margin:.35rem 0; }
th,td { border:1px solid var(--line); padding:.45rem .55rem; vertical-align:top; text-align:left; }
th { background:#eaf2fa; color:#173b60; }
tr:nth-child(even) td { background:#fbfdff; }
details { margin:1rem 0; padding:.65rem .85rem; border:1px solid var(--line); border-radius:.45rem; background:var(--panel); }
summary { cursor:pointer; font-weight:650; color:#173b60; }
.callout { border-left:5px solid var(--accent); background:var(--accent-soft); padding:.8rem 1rem; margin:1rem 0; }
.notice { color:var(--muted); font-style:italic; }
.file-list { padding-left:1.25rem; }
.file-list li { margin:.32rem 0; }
.file-meta { color:var(--muted); font-size:.85rem; }
.stat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(12rem,1fr)); gap:.7rem; margin:1rem 0; }
.stat { border:1px solid var(--line); border-radius:.45rem; padding:.75rem; background:var(--panel); }
.stat strong { display:block; font-size:1.3rem; color:#0b4f8a; }
.footer { margin-top:3rem; padding:1.5rem 0 3rem; border-top:1px solid var(--line); color:var(--muted); font-size:.9rem; }
@media (max-width:850px) { .layout { display:block; } nav.toc { position:static; max-height:none; margin:1rem 0 1.5rem; } .masthead { padding-top:2rem; } }
@media print { nav.toc,.skip-link,.download-panel { display:none !important; } body { font-size:10.5pt; } .layout { display:block; } a { color:inherit; } .masthead { color:#000; background:#fff; border-bottom:2px solid #000; } }
"""


def build(root: Path, output: Path) -> dict[str, object]:
    paper_path = root / "PAPER.md"
    if not paper_path.exists():
        raise FileNotFoundError(paper_path)
    markdown = paper_path.read_text(encoding="utf-8")
    paper_html, headings = render_markdown(markdown)
    # The page shell owns the single document-level H1.  Retain the manuscript
    # title in the article, but demote that duplicate source title to H2 so
    # keyboard and screen-reader heading navigation has one clear entry point.
    paper_html = re.sub(
        r'<h1 id="([^"]+)">',
        r'<h2 id="\1" class="manuscript-title">',
        paper_html,
        count=1,
    )
    used_ids = {ident for _level, _title, ident in headings}

    # Add a short reader-level contents list.  Keep the h1 out of the TOC and
    # include h2/h3 only so it remains usable on small screens.
    toc_items: list[str] = []
    for level, title, ident in headings:
        if level == 2:
            toc_items.append(f'<li><a href="#{ident}">{html.escape(title)}</a></li>')
        elif level == 3:
            toc_items.append(f'<li class="toc-sub"><a href="#{ident}">{html.escape(title)}</a></li>')
    toc = "<ol>" + "".join(toc_items) + "</ol>"

    selected_rows: dict[str, int] = {}
    score_tables: list[str] = []
    specs = [
        (
            "TOP10_NEEDS_ONLY_v3.csv",
            [("decision_rank", "Rank"), ("label", "Exact target"), ("language_tag", "Language tag"), ("population_base", "Population base"), ("intrinsic_need_median", "Median unmet need"), ("standard_compute_p50_fecu", "Compute p50 (FECU)")],
            "Top 10 needs-only targets (machine-readable view)",
            10,
        ),
        (
            "TOP10_COMPUTE_EFFICIENCY_v3.csv",
            [("decision_rank", "Rank"), ("label", "Exact target"), ("language_tag", "Language tag"), ("intrinsic_need_median", "Median unmet need"), ("standard_compute_p50_fecu", "Compute p50 (FECU)"), ("access_gain_per_compute_median", "Median gain/FECU")],
            "Top 10 standardized compute-efficiency targets",
            10,
        ),
        (
            "TOP10_STAGE_OPPORTUNITY_v3.csv",
            [("opportunity_rank", "Rank"), ("label", "Stage opportunity"), ("language_tag", "Language tag"), ("population_base", "Opportunity base"), ("intrinsic_need_median", "Median unmet need")],
            "Stage-opportunity lane",
            10,
        ),
    ]
    for filename, columns, caption, max_rows in specs:
        fragment, count = csv_table(root, root / "structured" / filename, columns, caption, max_rows)
        selected_rows[filename] = count
        score_tables.append(fragment)

    catalog, catalog_records = artifact_links(root, output)
    source_digest = sha256(paper_path)
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    score_path = root / "structured" / "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv"
    with score_path.open("r", encoding="utf-8", newline="") as f:
        score_rows = list(csv.DictReader(f))
    target_count = len(score_rows)
    direct_count = sum(row.get("order_lane") == "person_need" for row in score_rows)
    stage_count = sum(row.get("order_lane") == "stage_opportunity" for row in score_rows)
    unranked_count = sum(row.get("order_lane") == "unranked_context" for row in score_rows)
    with (root / "structured" / "open_resource_canon_map.json").open("r", encoding="utf-8") as f:
        canon_count = len(json.load(f).get("resources", []))

    # A few links are always useful in the landing panel.  They are only added
    # when the corresponding file exists, avoiding dead links on early builds.
    primary_files = [
        root / "PAPER.md",
        root / "PAPER.docx",
        root / "PAPER.pdf",
        root / "sources" / "REFERENCES_APA.md",
    ]
    primary_links: list[str] = []
    for p in primary_files:
        if p.exists():
            rel = rel_href(p, root, output.parent)
            primary_links.append(f'<li><a href="{html.escape(rel, quote=True)}"><code>{html.escape(p.name)}</code></a> <span class="file-meta">{p.stat().st_size:,} bytes · SHA-256 <code>{sha256(p)}</code></span></li>')

    # Find the title from the first h1, falling back to a stable literal.
    title = next((t for level, t, _ident in headings if level == 1), "Allocating AI Compute for Global Educational Access")
    body = f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Offline accessible reader for Allocating AI Compute for Global Educational Access">
<title>{html.escape(title)} — research reader</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="masthead">
  <div class="shell">
    <span class="badge">Evidence-bound research reader · offline-first</span>
    <h1>{html.escape(title)}</h1>
    <p>Accessible HTML rendering of the current manuscript and its machine-readable evidence. This page is generated from <code>PAPER.md</code>; the linked CSV/JSON files remain the reproducibility sources.</p>
    <p class="file-meta">Manuscript SHA-256: <code>{source_digest}</code> · generated {generated}</p>
  </div>
</header>
<div class="shell layout">
  <main id="main-content" tabindex="-1">
    <section class="panel download-panel" aria-labelledby="downloads-heading">
      <h2 id="downloads-heading">Reader files and evidence</h2>
      <p>Use the editable source, formatted editions, or the hash-indexed evidence tables. No external scripts, fonts, or network calls are required for this reader.</p>
      <ul class="file-list">{"".join(primary_links) if primary_links else '<li class="notice">Formatted DOCX/PDF and reference files will appear here when built.</li>'}</ul>
      <div class="stat-grid" aria-label="Current reproducibility snapshot">
        <div class="stat"><strong>{target_count:,}</strong><span>authority targets in the evidence freeze</span></div>
        <div class="stat"><strong>{direct_count}</strong><span>source-authorized direct-person targets</span></div>
        <div class="stat"><strong>{stage_count}</strong><span>separately comparable stage opportunities</span></div>
        <div class="stat"><strong>{unranked_count}</strong><span>visible unranked or contextual targets</span></div>
        <div class="stat"><strong>100</strong><span>rows in the complete direct-person Top 100</span></div>
        <div class="stat"><strong>{canon_count}</strong><span>records in the language-neutral open-resource canon</span></div>
      </div>
    </section>
    <section class="panel" id="machine-views" aria-labelledby="machine-views-heading">
      <h2 id="machine-views-heading">Machine-readable decision views</h2>
      <p>These compact tables are generated directly from the current structured CSVs. They are projections under the documented common-prior model, not observed global rankings; open the linked files below for full row-level provenance.</p>
      {"".join(score_tables)}
    </section>
    <section class="panel" id="evidence-files" aria-labelledby="evidence-files-heading">
      <h2 id="evidence-files-heading">Evidence file map</h2>
      {catalog}
    </section>
    <article id="paper" aria-labelledby="paper-heading">
      <h2 id="paper-heading">Manuscript</h2>
      {paper_html}
    </article>
  </main>
  <nav class="toc" aria-label="Manuscript contents">
    <h2>Contents</h2>
    {toc}
  </nav>
</div>
<footer class="footer"><div class="shell">Generated by <code>scripts/build_html_v1.py</code>. The HTML is a presentation layer; claims, caveats, source identities, and hashes are governed by the manuscript and evidence files linked above.</div></footer>
</body>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(body, encoding="utf-8", newline="\n")
    report = {
        "schema": "interlanguage/research-html-build/1.0.0",
        "generated_utc": generated,
        "source": {"path": "PAPER.md", "bytes": paper_path.stat().st_size, "sha256": source_digest},
        "output": {"path": rel_href(output, root, root), "bytes": output.stat().st_size, "sha256": sha256(output)},
        "headings": len(headings),
        "selected_table_rows": selected_rows,
        "catalog_records": len(catalog_records),
        "catalog": catalog_records,
        "validation": validate_html(root, output),
        "runtime": "python standard library only; no network access",
    }
    report_path = root / "qa" / "HTML_BUILD_REPORT_v1.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output.resolve() if args.output else root / "index.html")
    report = build(root, output)
    print(json.dumps({"output": report["output"], "source": report["source"], "selected_table_rows": report["selected_table_rows"], "catalog_records": report["catalog_records"]}, indent=2))


if __name__ == "__main__":
    main()
