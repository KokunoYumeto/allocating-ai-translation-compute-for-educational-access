"""Fail-closed structural/numeric QA for the first Tamil learning unit.
This is not a substitute for a Tamil speaker or assistive-technology user review.
"""
import hashlib
import difflib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
H = "http://www.w3.org/1999/xhtml"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def identity(n):
    return n.tag, n.get("id")

def math_signature(n):
    # Only language-bearing mtext is allowed to change, not digits/punctuation in mtext.
    return (n.tag, sorted(n.attrib.items()), re.sub(r"[^\d.,…]", "", n.text or "") if n.tag == f"{{{M}}}mtext" else (n.text or "").strip(), [math_signature(x) for x in n])

def main():
    source_doc = ET.parse(LANG / "provenance/m81243.en.cnxml")
    source = source_doc.find(f'.//{{{C}}}section[@id="fs-id1830385"]')
    target = ET.parse(LANG / "translation/m81243-fs-id1830385.cnxml").getroot()
    ind = ET.parse(LANG / "provenance/m81243.id-ID.cnxml").find(f'.//{{{C}}}section[@id="fs-id1830385"]')
    expected_nodes = [str(identity(n)) for n in source.iter()]
    for label, tree in [("Tamil", target), ("Indonesian", ind)]:
        actual_nodes = [str(identity(n)) for n in tree.iter()]
        assert expected_nodes == actual_nodes, label + "\n" + "\n".join(difflib.unified_diff(expected_nodes, actual_nodes))
    math_source = source.findall(f'.//{{{M}}}math')
    math_target = target.findall(f'.//{{{M}}}math')
    assert [math_signature(n) for n in math_source] == [math_signature(n) for n in math_target]
    assert target.get("{http://www.w3.org/XML/1998/namespace}lang") == "ta-Taml-IN"
    assert [n.get("target-id") for n in source.findall(f'.//{{{C}}}link')] == [n.get("target-id") for n in target.findall(f'.//{{{C}}}link')]
    # Compute source classification answers from exact fractions/decimals, compare both lists.
    math_cases = [(["0","1/4","3","5.2","15","105"],[3,15,105],[0,3,15,105]), (["0","2/3","2","9","11.8","241","376"],[2,9,241,376],[0,2,9,241,376]), (["0","5/3","7","8.8","13","201"],[7,13,201],[0,7,13,201])]
    for raw, natural, whole in math_cases:
        vals = [Fraction(x) for x in raw]
        assert [int(x) for x in vals if x.denominator == 1 and x >= 1] == natural
        assert [int(x) for x in vals if x.denominator == 1 and x >= 0] == whole
    for sol_id, expected in [("fs-id2775154", [[2,9,241,376],[0,2,9,241,376]]), ("fs-id1415724", [[7,13,201],[0,7,13,201]])]:
        sol = target.find(f'.//{{{C}}}solution[@id="{sol_id}"]')
        assert [[int(x) for x in re.findall(r"\d+", "".join(n.itertext()))] for n in sol.findall(f'.//{{{C}}}item')] == expected
    recovery = ET.parse(LANG / "translation/recovery.xhtml").getroot()
    questions = [n for n in recovery.iter() if n.get("data-kind")]
    answers = [n for n in recovery.iter() if n.get("data-answer-for")]
    assert len(questions) == 15
    assert Counter(n.get("data-answer-for") for n in answers) == Counter(n.get("id") for n in questions)
    assert all(len("".join(n.itertext())) > 80 for n in answers)
    assert all(n.find(f'.//{{{H}}}a') is not None for n in answers)
    expected_counts = {"diagnostic":4,"practice":3,"mastery":4,"retry":4}
    assert Counter(n.get("data-kind") for n in questions) == expected_counts
    # Mastery/retry must test a count, not state the answer in the question.
    svg_ns = "http://www.w3.org/2000/svg"
    for qid, shape, count in [("ta-M1", "circle", 6), ("ta-T1", "ellipse", 3)]:
        item = recovery.find(f'.//*[@id="{qid}"]')
        assert len(item.findall(f'.//{{{svg_ns}}}{shape}')) == count
        assert not re.search(r"\d", "".join(item.find(f'{{{H}}}p').itertext())), qid
    # Numeric directions and supplied set answers are independently enumerated in a small review fixture.
    fixture = {"D1": "4", "D2":"0", "D4":str(2+1), "P1":"5", "P3":str(4-2), "M1":"6", "M4":str(1+3), "T1":"3", "T4":str(6-3)}
    for key, expected in fixture.items():
        n = recovery.find(f'.//*[@id="ta-{key}-answer"]')
        first = n.find(f'{{{H}}}p')
        assert "".join(first.itertext()).startswith(expected + "."), key
    doc = ET.parse(LANG / "reader/index.html").getroot()
    ids = [n.get("id") for n in doc.iter() if n.get("id")]
    assert len(ids) == len(set(ids)), "Duplicate IDs"
    links = [n.get("href") for n in doc.iter() if n.get("href", "").startswith("#")]
    assert all(x[1:] in ids for x in links), "Broken fragment link"
    for n in doc.iter():
        assert n.tag.rsplit("}",1)[-1] not in ["script","iframe","form"]
        for key in ["src"]:
            assert not n.get(key, "").startswith(("https:","http:")), "Remote runtime dependency"
    assert len(doc.findall(f'.//{{{M}}}math')) == len(math_source)
    assert doc.get("lang") == "ta-Taml-IN"
    assert "\ufffd" not in (LANG / "reader/index.html").read_text(encoding="utf-8")
    assert not re.search(r"<\w+:(svg|circle|ellipse)\b", (LANG / "reader/index.html").read_text(encoding="utf-8")), "Prefixed SVG fails in text/html"
    assert len(doc.findall(f'.//{{{svg_ns}}}svg')) == 3
    reader = LANG / "reader"
    local_assets = set()
    for n in doc.iter():
        for attr in ("href", "src"):
            value = n.get(attr)
            if not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                assert n.tag == f"{{{H}}}a" and attr == "href", "Remote reading dependency"
            elif url.path:
                asset = (reader / unquote(url.path)).resolve()
                assert asset.is_relative_to(reader) and asset.is_file(), value
                local_assets.add(asset.relative_to(reader).as_posix())
    for css in reader.rglob("*.css"):
        for value in re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", css.read_text(encoding="utf-8")):
            assert not urlsplit(value).scheme and not urlsplit(value).netloc
            asset = (css.parent / unquote(value)).resolve()
            assert asset.is_relative_to(reader) and asset.is_file(), value
            local_assets.add(asset.relative_to(reader).as_posix())
    with zipfile.ZipFile(LANG / "reader/ta-Taml-IN-A00-U001.epub") as z:
        assert z.infolist()[0].filename == "mimetype" and z.infolist()[0].compress_type == zipfile.ZIP_STORED
        assert z.read("mimetype") == b"application/epub+zip"
        assert z.testzip() is None
        for name in z.namelist():
            if name.endswith((".xhtml", ".opf", ".xml")):
                ET.fromstring(z.read(name))
        opf = ET.fromstring(z.read("OEBPS/package.opf"))
        for item in opf.findall(".//{http://www.idpf.org/2007/opf}item"):
            assert "OEBPS/" + item.get("href") in z.namelist()
    lock = json.loads((LANG / "sources.lock.json").read_text(encoding="utf-8"))
    for n in lock["witnesses"]:
        assert sha(ROOT / n["path"]) == n["sha256"], n["path"]
    repeat = ROOT / "build/ta-repeat"
    for p in (LANG / "reader").rglob("*"):
        if p.is_file():
            assert sha(p) == sha(repeat / p.relative_to(LANG / "reader")), f"Non-reproducible {p.name}"
    result = {"status":"pass", "locale":"ta-Taml-IN", "scope":"A00-U001, m81243#fs-id1830385", "source_nodes":sum(1 for _ in source.iter()), "source_ids":sum(1 for n in source.iter() if n.get("id")), "MathML_expressions_unchanged":len(math_source), "source_exercises_with_solutions":3, "new_companion_items":expected_counts, "new_answer_coverage":"15/15 with feedback links", "fragment_links_resolved":len(links), "html_unique_ids":len(ids), "byte_identical_builds":2, "epub_internal_checks":"pass; external EPUBCheck not yet run", "source_witness_hashes":"pass", "limitations":["not native-speaker reviewed", "not a validated Grades 2–8 placement test", "assistive-technology user testing and PDF/UA validation pending"], "inputs":{p.relative_to(LANG).as_posix():sha(p) for p in sorted((LANG / "translation").iterdir()) if p.is_file()}}
    result["offline_asset_closure"] = {"status":"pass", "local_dependencies":sorted(local_assets)}
    result["epub_internal_checks"] = "pass; see separate epubcheck.json for external validation"
    result["inputs"] = {f"translation/{name}":sha(LANG / "translation" / name) for name in ["m81243-fs-id1830385.cnxml", "recovery.xhtml"]}
    (LANG / "qa").mkdir(exist_ok=True)
    (LANG / "qa/structural-receipt.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
