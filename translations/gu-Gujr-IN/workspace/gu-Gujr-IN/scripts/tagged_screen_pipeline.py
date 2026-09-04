"""Prepare an owned print derivative and repair actual Chromium formula tags.

Never changes the library or translation inputs. No PDF/UA certification is made.
Run with the local Python that provides lxml and pypdf.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

from lxml import etree, html
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, NameObject, TextStringObject

PREFIX = "GUFORMULA:"
PRINT_CSS = """
@page {size:A4; margin:15mm 15mm 17mm;}
@media print {
  html {font-size:14px;} body {font-size:11pt;line-height:1.65;background:white;}
  header,main,footer {width:auto;max-width:none;margin:0;padding:0;}
  header {padding-bottom:8mm;} h1 {font-size:22pt;line-height:1.5;}
  h2 {font-size:16pt;line-height:1.6;} h3 {font-size:12pt;}
  p {widows:3;orphans:3;} h1,h2,h3,h4,h5,h6 {break-after:avoid;}
  nav,.skip,.screen-only {display:none!important;}
  .source-paragraph {margin:.7rem 0;}
  p.source-paragraph {break-inside:avoid;}
  .source .example,.source .exercise,.source .solution,.source .note,
  .source .definition {break-inside:auto;}
  .source .problem,.source .definition {break-inside:avoid;}
  .source-media,figure {break-inside:avoid;}
  .source .item {padding:.5rem .7rem;margin:.55rem 0;}
  .source .solution {padding:.6rem .75rem;}
  .source .example {padding:.75rem;}
  .source .exercise:not(:has(table)):not(:has(.source-media)) {break-inside:avoid;}
  .figure-description {font-size:9pt;line-height:1.65;}
  .table-scroll {overflow:visible;max-width:none;}
  .table-scroll table {min-width:0;}
  .gu-place-redraw table[style*="flex"] {flex:1 1 0!important;min-width:0!important;width:0!important;font-size:12px!important;}
  .gu-place-redraw table[style*="flex"] th {overflow-wrap:normal!important;}
  .source table tr:first-child {break-after:avoid;}
  .localized-figure {max-height:65mm;}
  img {max-height:100mm;object-fit:contain;}
  math {font-size:1.12em;}
  a {color:inherit;}
  footer {font-size:8pt;line-height:1.6;}
}
"""


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def math_alt(el) -> str:
    """Explicit limited grammar; fail on new constructs rather than guess."""
    tag = etree.QName(el).localname
    children = list(el)
    if tag in {"math", "mrow", "mstyle", "mpadded", "semantics"}:
        return norm(" ".join(math_alt(c) for c in children if etree.QName(c).localname != "annotation"))
    if tag in {"mn", "mi", "mtext"}:
        return norm("".join(el.itertext())).replace("…", " અને આમ આગળ")
    if tag == "mo":
        token = norm("".join(el.itertext()))
        return {"+": "વત્તા", "−": "ઓછા", "-": "ઓછા", "=": "બરાબર",
                "×": "ગુણ્યા", "·": "ગુણ્યા", "÷": "ભાગ્યા", "…": "અને આમ આગળ",
                ">": "કરતાં મોટું", "<": "કરતાં નાનું"}.get(token, token)
    if tag == "mspace":
        return ""
    if tag == "mfrac" and len(children) == 2:
        return f"અપૂર્ણાંક (અંશ {math_alt(children[0])}; છેદ {math_alt(children[1])})"
    if tag == "msup" and len(children) == 2:
        return f"({math_alt(children[0])}) ની ઘાત ({math_alt(children[1])})"
    raise ValueError(f"Unreviewed MathML alternative grammar: {tag}")


def prepare(source: Path, output: Path, manifest_path: Path):
    root = html.fromstring(source.read_bytes())
    source_math = [etree.tostring(e, with_tail=False) for e in root.xpath("//math")]
    for e in root.xpath("//link[@href]"):
        p = (source.parent / e.get("href")).resolve()
        if not p.is_file(): raise FileNotFoundError(p)
        e.set("href", p.as_uri())
    for e in root.xpath("//img[@src]"):
        src = e.get("src")
        if not re.match(r"^[a-z]+:", src):
            p = (source.parent / src).resolve()
            if not p.is_file(): raise FileNotFoundError(p)
            e.set("src", p.as_uri())
    for e in root.xpath("//a[@href]"):
        href = e.get("href")
        if not href.startswith(("#", "http:", "https:", "mailto:")):
            e.set("href", (source.parent / href).resolve().as_uri())
    # Inline source paragraphs become real paragraphs. Containers with blocks
    # remain containers, so no invalid p/table nesting is introduced.
    converted = 0
    blocks = {"div", "p", "section", "figure", "table", "ul", "ol", "h1", "h2", "h3"}
    for e in root.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," source-paragraph ")]'):
        if not any(c.tag in blocks for c in e):
            e.tag = "p"
            converted += 1
    for e in root.xpath("//details"):
        e.set("open", "open")
    row_headers=0
    # Source teaching tables without column headings pair a left-hand verbal
    # instruction with its right-hand worked value. Expose that instruction as
    # a row header while retaining its normal source appearance.
    for table in root.xpath('//table[not(.//th)]'):
        for tr in table.xpath('./tbody/tr|./tr'):
            cells=list(tr)
            if len(cells)==2 and cells[0].tag=='td' and norm(cells[0].text_content()):
                cells[0].tag='th';cells[0].set('scope','row')
                cells[0].set('style',(cells[0].get('style','')+';font-weight:normal;background:inherit').lstrip(';'))
                row_headers+=1
    formulas = []
    for i, e in enumerate(root.xpath("//math"), 1):
        key = f"{PREFIX}{i:05d}"
        alt = math_alt(e)
        if not alt: raise ValueError(f"Empty formula {i}")
        formulas.append({"key": key, "alt": alt,
                         "mathml": etree.tostring(e, encoding="unicode", with_tail=False),
                         "source_ancestor_id": next((a.get("id") for a in e.iterancestors() if a.get("id")), None)})
        e.set("role", "img")
        e.set("aria-label", key)
    style = etree.SubElement(root.find("head"), "style")
    style.text = PRINT_CSS
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("<!doctype html>\n" + html.tostring(root, encoding="unicode"), encoding="utf-8")
    manifest = {
        "source": str(source.resolve()), "source_sha256": digest(source),
        "prepared_html": str(output.resolve()), "prepared_sha256": digest(output),
        "source_math_sha256": sha256(b"\n".join(source_math)).hexdigest(),
        "formulas": formulas, "paragraph_containers_converted": converted,
        "instruction_value_row_headers_added":row_headers,
        "source_counts": {"math":len(formulas),"headings":len(root.xpath("//h1|//h2|//h3|//h4|//h5|//h6")),
                          "media":len(root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," source-media ")]')),
                          "solutions":len(root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," solution ")]')),
                          "exercises":len(root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," exercise ")]'))},
        "decisions": ["Only the owned print derivative receives semantic attributes and print styles.",
                      "Native MathML and numbers/operators remain visually unchanged.",
                      "Formula alternatives use Gujarati operator words and explicit fraction numerator/denominator.",
                      "All source-provided solutions remain visible; separate added-answer companion is not included in this file."]}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest["source_counts"]))


def struct_walk(item):
    if isinstance(item, list):
        for child in item: yield from struct_walk(child)
    elif hasattr(item, "get_object"):
        obj = item.get_object()
        if hasattr(obj, "get") and obj.get("/Type") == "/StructElem":
            yield obj
            if "/K" in obj: yield from struct_walk(obj["/K"])


def mark_artifacts(page, writer):
    """Explicitly mark painting outside Chromium's tagged content as artifacts.

    This wraps existing untagged runs; it never deletes or changes painting
    operators. Existing top-level tagged runs and every MCID remain intact.
    """
    stream=ContentStream(page.get_contents(),writer)
    result=[];stack=[];artifact_open=False;count=0
    for operands,op in stream.operations:
        is_begin=op in (b"BDC",b"BMC")
        props=operands[1] if op==b"BDC" and len(operands)>1 else {}
        is_mcid=bool(hasattr(props,"get") and props.get("/MCID") is not None)
        if is_mcid:
            if stack:raise ValueError("Unexpected nested MCID; artifact wrapper needs review")
            if artifact_open:result.append(([],b"EMC"));artifact_open=False
        elif not stack and not artifact_open:
            result.append(([NameObject("/Artifact")],b"BMC"));artifact_open=True;count+=1
        result.append((operands,op))
        if is_begin:stack.append(is_mcid)
        elif op==b"EMC":
            if not stack:raise ValueError("Unbalanced original marked content")
            stack.pop()
    if stack:raise ValueError("Unclosed original marked content")
    if artifact_open:result.append(([],b"EMC"))
    old_paint=[x for x in stream.operations if x[1] not in (b"BDC",b"BMC",b"EMC")]
    new_paint=[x for x in result if x[1] not in (b"BDC",b"BMC",b"EMC")]
    if old_paint!=new_paint:raise ValueError("Artifact wrapping changed painting operators")
    stream.operations=result
    page.replace_contents(stream)
    return count


def finalize(raw: Path, output: Path, manifest_path: Path, receipt_path: Path):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {f["key"]: f["alt"] for f in manifest["formulas"]}
    reader = PdfReader(raw)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    root = writer.root_object
    if "/StructTreeRoot" not in root: raise ValueError("Missing actual structure tree")
    seen = []; figure_containers=0
    for obj in struct_walk(root["/StructTreeRoot"]["/K"]):
        alt = str(obj.get("/Alt", ""))
        if alt.startswith(PREFIX):
            if obj.get("/S") != "/Figure" or alt not in expected:
                raise ValueError(f"Unexpected tagged formula: {obj}")
            obj[NameObject("/S")] = NameObject("/Formula")
            obj[NameObject("/Alt")] = TextStringObject(expected[alt])
            seen.append(alt)
        elif obj.get("/S")=="/Figure" and not alt:
            # HTML figure containers hold semantic child tables/descriptions;
            # they are not separate images needing a second alternative.
            obj[NameObject("/S")]=NameObject("/Div")
            figure_containers+=1
    if Counter(seen) != Counter(expected.keys()):
        raise ValueError(f"Formula coverage mismatch: missing={set(expected)-set(seen)} duplicates={len(seen)-len(set(seen))}")
    root[NameObject("/Lang")] = TextStringObject("gu-Gujr-IN")
    artifact_runs=sum(mark_artifacts(p,writer) for p in writer.pages)
    portable_links=0
    for p in writer.pages:
        for a in p.get('/Annots',[]):
            a=a.get_object();action=a.get('/A')
            if action and str(action.get('/URI','')).startswith('file:'):
                uri=str(action['/URI'])
                if uri.endswith('/notices.html'):
                    action[NameObject('/URI')]=TextStringObject('../notices.html')
                    portable_links+=1
                else:raise ValueError(f'Unreviewed local PDF link: {uri}')
    writer.add_metadata({"/Title": reader.metadata.title or "ગુજરાતી ગણિત",
                         "/Subject": "Gujarati structured screen PDF; human language review pending; not certified PDF/UA",
                         "/Creator": "Local Gujarati tagged screen-PDF workflow"})
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.write(output)
    check = PdfReader(output)
    actual = list(struct_walk(check.trailer["/Root"]["/StructTreeRoot"]["/K"]))
    final_formulas = [e for e in actual if e.get("/S") == "/Formula"]
    if len(final_formulas) != len(expected): raise ValueError("Post-write formula mismatch")
    receipt = {"raw_sha256":digest(raw),"pdf_sha256":digest(output),"pages":len(check.pages),
               "source_sha256":manifest["source_sha256"],"formula_count":len(final_formulas),
               "structure_tags":dict(Counter(str(e.get("/S")) for e in actual)),
               "formula_alts_exact":Counter(str(e["/Alt"]) for e in final_formulas)==Counter(expected.values()),
               "semantic_figure_containers":figure_containers,"explicit_artifact_runs":artifact_runs,
               "portable_relative_notice_links":portable_links,
               "preserved": "Existing ParentTree, MCIDs, structure child relationships, outlines and page content cloned intact.",
               "limitations": ["No PDF/UA conformance certification.","Plain pypdf text extraction ignores some Gujarati ActualText replacements; Poppler is used for logical extraction QA."]}
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "finalize"])
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare": prepare(args.input, args.output, args.manifest)
    else:
        if not args.receipt: parser.error("finalize requires --receipt")
        finalize(args.input, args.output, args.manifest, args.receipt)
