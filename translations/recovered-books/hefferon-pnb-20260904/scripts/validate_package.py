"""Finite source/math/structure/language/asset checks for this opening package."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import etree as E
from lxml import html
from recovery_io import BASE, NOTICES, load, file_hash
from b40_opening_tex import convert, TexError
from b40_opening_math_expected import expected
from study_b40_toc import build_entries, legend_record

def require(test, message):
    if not test:
        raise AssertionError(message)

def descriptor(node):
    return [E.QName(node).localname, dict(node.attrib), node.text, [descriptor(c) for c in node]]

def main():
    m, t, repo = load()
    reader = BASE / "reader/opening.html"
    raw = reader.read_bytes()
    doc = html.fromstring(raw)
    require(doc.get("lang") == "pnb-Arab-PK" and doc.get("dir") == "rtl", "Locale/direction")
    ids = doc.xpath("//@id")
    require(len(ids) == len(set(ids)), "Duplicate IDs")
    require(not doc.xpath("//script|//iframe|//object|//embed"), "Executable content")
    owners = doc.xpath('//*[@id="b40-opening-source"]//*[@data-source-key]')
    require(len(owners) == 174, "Source owner count")
    require(set(x.get("data-source-key") for x in owners) == set(m["expected_source_keys"]), "Source owner set")
    owner_map = {x.get("data-source-key"): x for x in owners}
    notices = json.loads(NOTICES.read_text(encoding="utf-8"))
    math_count = 0
    for b in m["source_blocks"]:
        source = (repo / b["source_file"]).read_text(encoding="utf-8")
        require(source[b["source_start"]:b["source_end"]] == b["source_raw"], "Source span " + b["key"])
        require(hashlib.sha256(b["source_raw"].encode()).hexdigest() == b["source_raw_sha256"], "Span hash")
        node = owner_map[b["key"]]
        require(node.get("data-source-raw-sha256") == b["source_raw_sha256"], "Rendered span binding")
        tokens = re.findall(r"\{\{(?:tex|url|include|mark):\d+\}\}", t["source_blocks"][b["key"]])
        require(tokens == [s["token"] for s in b["slots"]], "Placeholder order " + b["key"])
        for slot in b["slots"]:
            found = node.xpath('.//*[@data-source-slot-token=$token]', token=slot["token"])
            # Included date is itself a source owner but has no nested formula slots.
            require(len(found) == 1, "Rendered slot count")
            rendered = found[0]
            if slot["kind"] == "tex":
                math_count += 1
                require(rendered.get("data-source-tex") == slot["value"] and rendered.get("data-source-tex-raw") == slot["raw"], "TeX changed")
                _, converted = convert(slot["value"])
                require(converted["tree"] == expected(slot["value"]), "Independent math fixture")
                ast = rendered.xpath('./math/semantics/mrow')[0]
                require(descriptor(ast) == expected(slot["value"]), "Rendered MathML tree")
                require(rendered.xpath('string(./math/semantics/annotation)') == slot["value"], "TeX annotation")
                require("".join(x["raw"] for x in converted["tokens"]) == slot["value"], "Token replay")
    require(math_count == 76, "Formula count")
    for item in notices["macro_evidence"]["selected_ranges"]:
        lines = (repo / notices["macro_evidence"]["file"]["repository_path"]).read_text(encoding="utf-8").splitlines(keepends=True)
        a, b = item["lines"]
        require("".join(lines[a-1:b]) == item["raw"], "Pinned macro expansion witness")
    tc = json.loads((BASE / "translations/b40-contents-pnb.json").read_text(encoding="utf-8"))
    study = json.loads((BASE / "source-excerpts/b40-toc-source-study.json").read_text(encoding="utf-8"))
    entries = build_entries(repo / "src")
    require(entries == study["canonical_entries"], "Pinned contents source replay")
    require(legend_record(repo / "src") == study["legend"]["canonical"], "Legend source replay")
    rows = doc.xpath('//*[@data-toc-owner]')
    require([x.get("data-toc-owner") for x in rows] == list(tc["titles"]) == [e["owner"] for e in entries], "All 97 titles/order")
    require(len(rows) == 97, "Contents count")
    for row, entry in zip(rows, entries):
        require(row.get("data-optional") == str(entry["optional_star"]).lower(), "Optional flag")
        require(len(row.xpath('.//sup[@class="optional-star"]')) == int(entry["optional_star"]), "Optional display marker")
        if entry["kind"] not in {"chapter", "topic"} and entry["generated_label"]:
            require(row.xpath('string(./bdi[@class="toc-label"])') == entry["generated_label"], "Source numbering")
    require(len(doc.xpath('//sup[@class="optional-star"]')) == 14, "14 optional markers")
    require(doc.xpath('string(//*[@id="toc-legend"])').strip() == '* ' + tc["legend"], "Translated legend")
    require(len(doc.xpath('//*[@data-origin="original-worked-example"]')) == 4, "Four examples")
    require(all(doc.xpath('//*[@id=$id]', id="bridge-q" + str(i)) and doc.xpath('//*[@id=$id]', id="bridge-a" + str(i)) for i in range(1,9)), "Eight question-answer pairs")
    require(len(doc.xpath('//*[@id="bridge-glossary"]//tbody/tr')) == 9, "Nine glossary rows")
    require(len(doc.xpath('//*[@id="bridge-glossary"]//tbody/tr/td[@lang="ur"]')) == 9, "Urdu help separated")
    for node in doc.xpath('//bdi|//math'):
        require(node.get("dir") == "ltr", "Math/LTR isolation")
    text = " ".join(doc.xpath('//body//text()[not(ancestor::style)]'))
    require(not re.search(r"[\u0900-\u0dff\ufffd]", text), "Unexpected script/replacement glyph")
    require(not re.search(r"\{\{(?:tex|url|include|mark):", text), "Unresolved placeholders")
    require("کالمਾਂ" not in text, "Mixed-script typo")
    for node in doc.xpath('//img'):
        require(bool(node.get("alt", "").strip()), "Missing image alternative")
    linked = []
    for node in doc.xpath('//*[@href or @src]'):
        value = node.get("href") or node.get("src")
        url = urlsplit(value)
        if url.scheme or url.netloc:
            require(url.scheme in {"https", "http"}, "Unsafe external URL")
            continue
        if url.path:
            path = (reader.parent / unquote(url.path)).resolve()
            require(path.is_relative_to(BASE.resolve()), "Escaping local path")
            require(path.exists() or path == BASE / "qa/validation.json", "Missing local link: " + value)
            linked.append(path.relative_to(BASE).as_posix())
        elif url.fragment:
            require(url.fragment in ids, "Unresolved fragment: " + value)
    svg = E.parse(str(BASE / "assets/bridge-system.svg"))
    require(svg.xpath('count(//*[local-name()="circle"][@cx="320"][@cy="225"])') == 1, "Intersection coordinate")
    require(4 + 3 == 7 and 4 - 3 == 1, "Graph intersection mathematics")
    require('M60,45 L515,360' in (BASE / "assets/bridge-system.svg").read_text() and 'M125,360 L580,45' in (BASE / "assets/bridge-system.svg").read_text(), "Plot endpoints")
    # Independent arithmetic safeguards, coupled to the visible postimages below.
    arithmetic = [(3*4+2 == 14), (4+3 == 7 and 4-3 == 1), ((1+3,2-1)==(4,1) and (2-3,4+1)==(-1,5)), ((1*2+2,3*2+4)==(4,10)), (2*3+5==11), (2*3+1==7 and 3-1==2), (2+3==5 and 2*2+3!=8), ((-1+4,3+2)==(3,5)), ((-2*2,-2*-3)==(-4,6)), ((2*1+0*2,-1*1+3*2)==(2,5)), (2!=3), all((v+2-v==2 and 2*v+2*(2-v)==4) for v in [-10,-1,0,1,7])]
    require(all(arithmetic) and len(arithmetic)==12, "Worked arithmetic")
    for ident, result in [("bridge-example-1","x = 4"),("bridge-example-2","(4,3)"),("bridge-example-3","(−1,5)"),("bridge-a1","x=3"),("bridge-a2","(3,1)"),("bridge-a3","7 ≠ 8"),("bridge-a4","(3,5)"),("bridge-a5","(−4,6)"),("bridge-a8","(t,2−t)")]:
        require(result in doc.xpath('string(//*[@id=$id])', id=ident), "Visible answer differs: " + ident)
    rejected = []
    for malformed in [r"\unknown{x}", "x^{", "x^^2", "x/y"]:
        try:
            convert(malformed)
        except (TexError, ValueError):
            rejected.append(malformed)
    require(len(rejected) == 4, "Unknown TeX fails closed")
    report = {"status":"PASS", "reader_sha256":file_hash(reader), "reader_bytes":len(raw), "source_slots":174,
              "source_span_checks":174, "unchanged_formula_owners_with_independent_fixtures":76,
              "contents_entries_reconstructed":97, "optional_markers":14, "new_math_checks":12,
              "original_examples":4, "exercise_answer_pairs":8, "urdu_glossary_rows":9,
              "all_ids_unique":True, "fragment_closure":True, "local_assets_and_links":sorted(set(linked)),
              "unknown_tex_rejected":rejected, "gurmukhi_or_replacement_glyphs":0,
              "visual_qa":"Separate browser/PDF evidence required; this check is structural and symbolic, not a visual or native-fluency certificate."}
    (BASE / "qa/validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:report[k] for k in ["status","reader_sha256","source_slots","contents_entries_reconstructed","new_math_checks"]}))

if __name__ == "__main__":
    main()
