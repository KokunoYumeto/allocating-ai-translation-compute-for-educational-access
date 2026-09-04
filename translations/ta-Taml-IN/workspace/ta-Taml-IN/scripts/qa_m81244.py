"""Source-only checks for completed addition fragments; no module completion claim."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

sys.dont_write_bytecode = True
from build_u002 import require
from qa_source_coverage import signature, stable_attributes

LANG = Path(__file__).resolve().parents[1]
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
S = "{http://www.w3.org/2000/svg}"
XL = "{http://www.w3.org/XML/1998/namespace}lang"
SPANS = {"frontmatter": (14, 2, 0, 0, 0, 0), "fs-id2299412": (18, 8, 2, 1, 1, 1),
         "fs-id1122444": (13, 6, 1, 1, 1, 0), "fs-id2601285": (143, 30, 19, 3, 3, 0),
         "fs-id2145437": (322, 86, 30, 9, 9, 19), "fs-id1385496": (1480, 163, 135, 21, 21, 5),
         "fs-id2691382": (273, 41, 52, 6, 6, 0), "fs-id2197427": (210, 46, 16, 6, 6, 3),
         "fs-id1611455": (81, 6, 11, 0, 0, 0)}
ASSET_DIRS = {"fs-id2299412": "m81244-readiness", "fs-id2145437": "u010", "fs-id1385496": "u011", "fs-id2197427": "u013"}
WITNESSES = {"en": "b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b",
             "id-ID": "d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(target, source):
    require([(n.tag, len(n)) for n in target.iter()] == [(n.tag, len(n)) for n in source.iter()], "Hierarchy differs")
    def structural(n):
        attrs = stable_attributes(n)
        if n.tag == C + "table":
            attrs.pop("summary", None)
        return attrs
    require([structural(n) for n in target.iter()] == [structural(n) for n in source.iter()], "Source attributes differ")
    require([signature(n) for n in target.iter(M + "math")] == [signature(n) for n in source.iter(M + "math")], "Mathematics differs")
    for a, b in zip(target.iter(M + "mtext"), source.iter(M + "mtext")):
        expected = {"base-10": "அடிமானம்-10", "basis-10": "அடிமானம்-10", "Basis-10": "அடிமானம்-10", "and": "மற்றும்", "dan": "மற்றும்"}.get(b.text, b.text)
        require(a.text == expected, "MathML mtext differs outside declared language localizations")
    for left, right in zip(target.iter(M + "math"), source.iter(M + "math")):
        for a, b in zip(left.iter(), right.iter()):
            significant = lambda value: value if value and value.strip() else ""
            if a.tag != M + "mtext":
                require(significant(a.text) == significant(b.text), "MathML non-language text differs")
            if a is not left:
                require(significant(a.tail) == significant(b.tail), "MathML internal tail differs")
    # Keep text-node boundaries: concatenating adjacent MathML/paragraph nodes
    # can invent a numeral such as 23 from separately authored 2 and 3.
    digits = lambda node: [value for text in node.itertext() for value in re.findall(r"[0-9]+", text)]
    require(digits(target) == digits(source), "Body digit sequence differs")


def source_fragment(root, sid):
    if sid != "frontmatter":
        found = next((n for n in root.find(C + "content") if n.get("id") == sid), None)
        require(found is not None, "Source span is not a direct content child")
        return found
    fragment = ET.Element(C + "document")
    for name in ("title", "metadata"):
        fragment.append(copy.deepcopy(root.find(C + name)))
    return fragment


def check():
    paths = {locale: LANG / f"provenance/m81244.{locale}.cnxml" for locale in WITNESSES}
    for locale, path in paths.items():
        require(sha(path) == WITNESSES[locale], "Pinned witness differs: " + locale)
    roots = {locale: ET.parse(path).getroot() for locale, path in paths.items()}
    records = []
    inputs = {p.relative_to(LANG).as_posix(): sha(p) for p in paths.values()}
    for script in (Path(__file__), LANG / "scripts/qa_source_coverage.py", LANG / "scripts/build_u002.py"):
        inputs[script.relative_to(LANG).as_posix()] = sha(script)
    all_source_ids, all_svg_ids = [], []
    previous_module = LANG / "translation/m81243.cnxml"
    inputs[previous_module.relative_to(LANG).as_posix()] = sha(previous_module)
    previous_module_ids = {n.get("id") for n in ET.parse(previous_module).getroot().iter() if n.get("id")}
    module_ids = {n.get("id") for n in roots["en"].iter() if n.get("id")}
    for sid, expected_counts in SPANS.items():
        path = LANG / f"translation/m81244-{sid}.cnxml"
        inputs[path.relative_to(LANG).as_posix()] = sha(path)
        target = ET.parse(path).getroot()
        sources = {locale: source_fragment(root, sid) for locale, root in roots.items()}
        require(target.get(XL) == "ta-Taml-IN", "Wrong locale")
        ids = [n.get("id") for n in target.iter() if n.get("id")]
        require(len(ids) == len(set(ids)), "Duplicate source IDs")
        counts = (len(list(target.iter())), len(ids), len(list(target.iter(M + "math"))),
                  len(list(target.iter(C + "exercise"))), len(list(target.iter(C + "solution"))), len(list(target.iter(C + "media"))))
        require(counts == expected_counts, "Unexpected span counts")
        for source in sources.values():
            compare(target, source)
        all_source_ids += ids
        if sid == "frontmatter":
            md = "{http://cnx.rice.edu/mdml}"
            for name in ("content-id", "uuid"):
                require(all(target.find('.//' + md + name).text == source.find('.//' + md + name).text for source in sources.values()), "Module identity differs")
            objectives = list(target.find('.//' + C + "list"))
            for i, section_id in enumerate(("fs-id2601285", "fs-id2145437", "fs-id1385496", "fs-id2691382", "fs-id2197427")):
                section = ET.parse(LANG / f"translation/m81244-{section_id}.cnxml").getroot()
                require(objectives[i].text == section.find(C + "title").text, "Objective/section title differs")
        links = []
        for link in target.iter(C + "link"):
            target_id, document = link.get("target-id"), link.get("document", "m81244")
            if target_id:
                require(document in {"m81243", "m81244"}, "Unsupported linked source module")
                require(target_id in (previous_module_ids if document == "m81243" else module_ids), "Unresolved source target")
                links.append({"document": document, "target_id": target_id, "rendering": "module-aware reader mapping pending"})
            elif link.get("url"):
                parsed = urlparse(link.get("url"))
                require(parsed.scheme in {"http", "https"} and parsed.netloc, "Unsupported source URL")
                links.append({"url": link.get("url"), "rendering": "optional source resource, not an offline dependency"})
        tables = []
        for table in target.iter(C + "table"):
            for group in table.iter(C + "tgroup"):
                actual = sorted({len(row.findall(C + "entry")) for row in group.iter(C + "row")})
                tables.append({"id": table.get("id"), "declared_columns": int(group.get("cols")), "actual_row_cell_counts": actual})
        english_images = list(sources["en"].iter(C + "image"))
        medias, svg_ids = [], []
        for media, original in zip(target.iter(C + "media"), english_images):
            image = media.find(C + "image")
            asset = (path.parent / image.get("src")).resolve()
            require(asset.is_relative_to((LANG / "assets" / ASSET_DIRS[sid]).resolve()) and asset.is_file(), "Missing/out-of-scope redraw")
            require(asset.name == Path(original.get("src")).stem + ".svg" and image.get("mime-type") == "image/svg+xml", "Source image identity differs")
            inputs[asset.relative_to(LANG).as_posix()] = sha(asset)
            svg = ET.parse(asset).getroot()
            require(svg.tag == S + "svg" and svg.find(S + "desc").text == media.get("alt"), "Redraw/source description differs")
            all_ids = [n.get("id") for n in svg.iter() if n.get("id")]
            require(len(all_ids) == len(set(all_ids)), "Duplicate figure ID")
            svg_ids += all_ids
            for n in svg.iter():
                require(n.tag.rsplit("}", 1)[-1] not in {"script", "foreignObject", "image"}, "Unexpected active/external figure content")
                require(not any(k.lower().startswith("on") for k in n.attrib), "Figure event handler")
                for attr in ("aria-labelledby", "aria-describedby"):
                    require(all(i in all_ids for i in n.get(attr, "").split()), "Broken figure label reference")
            medias.append({"id": media.get("id"), "original": original.get("src"), "redraw": asset.relative_to(LANG).as_posix(), "sha256": sha(asset)})
        require(len(svg_ids) == len(set(svg_ids)), "Cross-figure ID collision")
        all_svg_ids += svg_ids
        records.append({"source_id": sid, "translation_sha256": sha(path), "counts": dict(zip(("elements", "ids", "mathml", "exercises", "solutions", "media"), counts)), "media": medias, "links": links, "tables": tables})
    require(len(all_source_ids) == len(set(all_source_ids)), "Cross-fragment source ID collision")
    require(len(all_svg_ids) == len(set(all_svg_ids)), "Cross-fragment SVG ID collision")
    # These fixtures must fail for their targeted reason, not because of a parser error.
    target = ET.parse(LANG / "translation/m81244-fs-id2601285.cnxml").getroot()
    source = roots["en"].find(f'.//{C}section[@id="fs-id2601285"]')
    cases = []
    changed = copy.deepcopy(target)
    changed.find('.//' + M + "mn").text = "9"
    cases.append((changed, "Mathematics differs"))
    changed = copy.deepcopy(target)
    changed.find('.//' + C + "para").set("id", "wrong")
    cases.append((changed, "Source attributes differ"))
    changed = copy.deepcopy(target)
    first, second = changed[1], changed[2]
    changed.remove(second)
    first.append(second)
    require([n.tag for n in changed.iter()] == [n.tag for n in target.iter()], "Preorder fixture changed tag order")
    cases.append((changed, "Hierarchy differs"))
    cases = [(changed, source, reason) for changed, reason in cases]
    target = ET.parse(LANG / "translation/m81244-fs-id1385496.cnxml").getroot()
    source = source_fragment(roots["en"], "fs-id1385496")
    changed = copy.deepcopy(target)
    changed.find('.//' + M + "mtext").text = ""
    cases.append((changed, source, "MathML mtext differs outside declared language localizations"))
    changed = copy.deepcopy(target)
    changed.find('.//' + C + "tgroup").set("cols", "12")
    cases.append((changed, source, "Source attributes differ"))
    changed = copy.deepcopy(target)
    changed.find('.//' + M + "math")[0].tail = "+"
    cases.append((changed, source, "MathML internal tail differs"))
    for changed, source, reason in cases:
        try:
            compare(changed, source)
        except ValueError as exc:
            require(reason == str(exc), "Negative fixture failed for unrelated reason")
        else:
            raise ValueError("Negative fixture accepted")
    require(all(sha(LANG / p) == digest for p, digest in inputs.items()), "Input changed during check")
    return {"status": "frontmatter-readiness-five-source-sections-key-concepts-checked-not-complete-module", "module": "m81244", "locale": "ta-Taml-IN",
            "inputs": inputs, "sections": records, "negative_tests": [r for _, _, r in cases],
            "totals": {key: sum(record["counts"][key] for record in records) for key in records[0]["counts"]},
            "unique_redraw_ids": len(all_svg_ids),
            "next_contiguous_section": "fs-id2263283", "limits": ["Section exercises and glossary excluded. All five translated objective headings now match their corresponding source drafts.",
            "Rendered review, companion routing, native and learner review remain separate.",
            "Tree/digit checks do not independently certify every Tamil word or redraw geometry; see author/figure notes."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check current receipt bytes without writing")
    args = parser.parse_args()
    receipt = check()
    raw = (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path = LANG / "qa/M81244-source-receipt.json"
    if args.check:
        require(path.read_bytes() == raw, "Source receipt is stale")
    else:
        path.write_bytes(raw)
    print(json.dumps({"mode": "check" if args.check else "write", "fragments": len(receipt["sections"]), "totals": receipt["totals"], "unique_redraw_ids": receipt["unique_redraw_ids"], "next": receipt["next_contiguous_section"], "negative_tests": receipt["negative_tests"]}, indent=2))


if __name__ == "__main__":
    main()
