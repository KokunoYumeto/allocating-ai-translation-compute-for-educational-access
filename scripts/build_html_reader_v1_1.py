#!/usr/bin/env python3
"""Render PAPER.md as a self-contained, keyboard-readable HTML document.

No remote mutation. Long appendix tables become labelled records, preserving
every cell in source order; short comparative tables remain scrollable tables.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

from lxml import etree, html

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PAPER.md"
OUT = ROOT / "staging" / "reader_surface_v1_1" / "index.html"
REPORT = ROOT / "HTML_READER_V1_1_VALIDATION.json"

CSS = """
:root{color-scheme:light dark;--paper:#fffdf8;--ink:#18202a;--muted:#59636d;--line:#d4d8dc;--accent:#145784;--wash:#eaf3f9}
*{box-sizing:border-box}html{scroll-padding-top:6rem}body{margin:0;background:#eeeae3;color:var(--ink);font:18px/1.65 Georgia,serif;overflow-wrap:anywhere}
a{color:var(--accent);text-underline-offset:.16em;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #dc9e25;outline-offset:4px}
.skip{position:absolute;top:-10rem}.skip:focus{top:0;z-index:99;background:white;padding:1rem}.reader-banner{position:sticky;top:0;z-index:5;background:var(--wash);border-bottom:1px solid var(--line);padding:.6rem 1rem;font:15px/1.5 system-ui,sans-serif;display:flex;gap:.5rem 1.2rem;flex-wrap:wrap}.reader-banner strong{margin-right:auto}
.layout{max-width:100rem;margin:auto;display:grid;grid-template-columns:17rem minmax(0,1fr);gap:1rem;padding:1.5rem}#TOC{align-self:start;position:sticky;top:5rem;max-height:calc(100vh - 6rem);overflow:auto;font:14px/1.45 system-ui,sans-serif;padding:1rem;background:var(--paper);border-radius:.5rem}#TOC ul{padding-left:1.2rem}#TOC li{margin:.45rem 0}
main{min-width:0;background:var(--paper);padding:2rem 3rem;border-radius:.5rem}h1,h2,h3,h4{font-family:system-ui,sans-serif;line-height:1.25;scroll-margin-top:6rem}h1{font-size:clamp(1.8rem,4vw,3rem);letter-spacing:-.025em}h2{margin-top:2.4rem;color:var(--accent)}h3{margin-top:1.8rem}p,main>section>p{max-width:76ch}li{margin:.4rem 0}code{font-size:.87em;overflow-wrap:anywhere;background:var(--wash);padding:.1em .2em}pre{white-space:pre-wrap;overflow-wrap:anywhere}blockquote{border-left:4px solid var(--accent);padding-left:1rem;color:var(--muted)}img{max-width:100%;height:auto}
.table-scroll{max-width:100%;overflow:auto;margin:1.5rem 0;border:1px solid var(--line)}table{border-collapse:collapse;min-width:48rem;font:14px/1.5 system-ui,sans-serif}th,td{padding:.75rem;border:1px solid var(--line);vertical-align:top;text-align:left}th{background:var(--wash);position:sticky;top:0}td{min-width:6rem;max-width:30rem;overflow-wrap:anywhere}
.records{display:grid;gap:1.5rem}.record{border-top:2px solid var(--line);padding-top:1rem}.record h3{margin:.4rem 0 1rem}.record dl{display:grid;grid-template-columns:minmax(8rem,12rem) minmax(0,1fr);margin:0;gap:.55rem 1rem;font-size:16px}.record dt{font:600 14px/1.5 system-ui,sans-serif;color:var(--muted)}.record dd{margin:0;overflow-wrap:anywhere}.record dd p{margin:0}footer{font:14px/1.5 system-ui,sans-serif;padding:2rem;color:var(--muted);max-width:90rem;margin:auto}
@media(max-width:1050px){.layout{grid-template-columns:1fr;padding:1rem}#TOC{position:static;max-height:18rem}main{padding:1.5rem}}@media(max-width:600px){body{font-size:17px}.layout{padding:.5rem}main{padding:1rem}.record dl{grid-template-columns:1fr;gap:.2rem}.record dd{margin-bottom:.8rem}.reader-banner{position:static}html{scroll-padding-top:1rem}.table-scroll{font-size:14px}}
@media(prefers-color-scheme:dark){:root{--paper:#171d22;--ink:#e8edf1;--muted:#b6c0c8;--line:#46515b;--accent:#a0d3f4;--wash:#263b49}body{background:#0d1115}}
@media print{.reader-banner,#TOC,.skip,footer{display:none}.layout{display:block;padding:0}main{padding:0}.table-scroll{overflow:visible}table{min-width:0;font-size:9pt}.record{break-inside:avoid}body{font-size:11pt;background:white;color:black}}
"""


def text_of(node):
    return " ".join("".join(node.itertext()).split())


def main():
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("Pandoc unavailable")
    result = subprocess.run([
        pandoc, str(SOURCE), "--from=markdown", "--to=html5", "--standalone",
        "--toc", "--toc-depth=3", "--section-divs", "--mathml",
        "--metadata=pagetitle:Allocating AI Translation Compute for Marginal Educational Access",
    ], capture_output=True, check=True)
    doc = html.document_fromstring(result.stdout)
    doc.set("lang", "en")
    head = doc.find("head")
    for style in list(head.findall("style")):
        head.remove(style)
    style = etree.SubElement(head, "style")
    style.text = CSS
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    etree.SubElement(head, "meta", name="source-sha256", content=source_hash)
    body = doc.find("body")
    original_children = list(body)
    for child in original_children:
        body.remove(child)
    skip = etree.SubElement(body, "a", href="#paper", attrib={"class":"skip"})
    skip.text = "Skip to paper"
    banner = etree.SubElement(body, "nav", attrib={"class":"reader-banner", "aria-label":"Publication and reader controls"})
    etree.SubElement(banner, "strong").text = "Readable web edition · Research report v1.1.0"
    for label, url in [
        ("Download the PDF", "PAPER.pdf"), ("Editable DOCX", "PAPER.docx"),
        ("Markdown source", "PAPER.md"), ("Contents", "#TOC"),
        ("DOI and versions", "https://doi.org/10.5281/zenodo.22172595"),
        ("Repository and data", "https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access"),
    ]:
        etree.SubElement(banner,"a",href=url).text=label
    layout=etree.SubElement(body,"div",attrib={"class":"layout"})
    toc=next((c for c in original_children if c.get("id")=="TOC"),None)
    if toc is not None:
        toc.set("aria-label","Contents")
        layout.append(toc)
    article=etree.SubElement(layout,"main",id="paper",tabindex="-1")
    for child in original_children:
        if child is not toc:
            article.append(child)

    table_log=[]
    for index, table in enumerate(list(article.iter("table")),1):
        headers=[text_of(c) for c in table.xpath("./thead/tr/th")]
        rows=table.xpath("./tbody/tr")
        before=[[text_of(c) for c in row] for row in rows]
        parent=table.getparent()
        mean_cell_characters = sum(len(cell) for row in before for cell in row) / max(1, sum(len(row) for row in before))
        prose_heavy = len(headers) >= 5 and mean_cell_characters > 70
        if len(rows)>=50 or prose_heavy:
            records=etree.Element("div",attrib={"class":"records", "role":"list"})
            for i,row in enumerate(rows,1):
                card=etree.SubElement(records,"article",attrib={"class":"record","role":"listitem"})
                title=etree.SubElement(card,"h3")
                title.text=" · ".join(text_of(c) for c in list(row)[:2])
                dl=etree.SubElement(card,"dl")
                for heading,cell in zip(headers,row):
                    etree.SubElement(dl,"dt").text=heading
                    dd=etree.SubElement(dl,"dd")
                    dd.text=cell.text
                    for child in cell:
                        dd.append(copy.deepcopy(child))
            after=[[text_of(c) for c in record.xpath("./dl/dd")] for record in records]
            assert before==after, f"Table {index} cell content changed during card conversion"
            parent.replace(table,records)
            form="labelled_records"
        else:
            wrap=etree.Element("div",attrib={"class":"table-scroll","role":"region","aria-label":f"Table {index}: scroll horizontally if needed","tabindex":"0"})
            parent.replace(table,wrap)
            wrap.append(table)
            for th in table.xpath("./thead/tr/th"):
                th.set("scope","col")
            form="scrollable_table"
        table_log.append({"table":index,"rows":len(rows),"columns":len(headers),"form":form,
                          "mean_cell_characters":round(mean_cell_characters,2),
                          "prose_heavy":prose_heavy,"cell_roundtrip":True})
    footer=etree.SubElement(body,"footer")
    footer.text="Self-contained HTML: no login, external fonts, scripts or network requests are required to read this downloaded file. Source SHA-256: "+source_hash
    data=etree.tostring(doc,method="html",encoding="utf-8",doctype="<!doctype html>")
    assert b"C:\\Users\\" not in data
    assert not doc.xpath("//script[@src] | //link[@rel='stylesheet']")
    ids=doc.xpath("//*[@id]/@id")
    assert len(ids)==len(set(ids)), "Duplicate heading IDs"
    broken=[a.get("href") for a in doc.xpath("//a[starts-with(@href,'#')]") if a.get("href")[1:] not in ids]
    assert not broken, broken
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_bytes(data)
    report={"schema":"research-paper-html/1.1", "status":"STRUCTURAL_PASS_VISUAL_REVIEW_PENDING",
            "source_sha256":source_hash,"html_sha256":hashlib.sha256(data).hexdigest(),"html_bytes":len(data),
            "tables":table_log,"broken_internal_links":broken,"external_runtime_dependencies":0}
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
