"""Structural, MathML and accessibility QA for A10 m82463."""
from pathlib import Path
import hashlib
import json
import re
from lxml import etree
from qa_a10_m82463_math import run as run_math_checks

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82463/index.cnxml"
GU = HERE / "a10-m82463.gu.cnxml"
ERRATA = HERE / "a10-m82463-errata.gu.json"
OUT = HERE.parent / "reviews/a10-m82463-qa.json"
SOURCE_SHA = "b6345a5a6a99108f9d32d6518445a4ae70a6b0c54a258021dffc6f2b77b8278a"
MATH = "http://www.w3.org/1998/Math/MathML"
CNX = "http://cnx.rice.edu/cnxml"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(SRC) == SOURCE_SHA
    source = etree.parse(str(SRC)).getroot()
    target = etree.parse(str(GU)).getroot()
    se = list(source.iter())
    ge = list(target.iter())
    assert len(se) == len(ge) == 3249
    assert [(etree.QName(x).namespace, etree.QName(x).localname) for x in se] == [
        (etree.QName(x).namespace, etree.QName(x).localname) for x in ge
    ]
    assert [x.get("id") for x in se] == [x.get("id") for x in ge]
    ids = [x.get("id") for x in ge if x.get("id")]
    assert len(ids) == len(set(ids)) == 711
    for a, b in zip(se, ge):
        for attr, value in a.attrib.items():
            if etree.QName(attr).localname in {"alt", "aria-label", "summary", "title"}:
                if re.search(r"[A-Za-z]", value):
                    assert re.search(r"[\u0a80-\u0aff]", b.get(attr, "")), (a.get("id"), attr)
            else:
                assert b.get(attr) == value, (a.get("id"), attr)
        if etree.QName(a).namespace == MATH and etree.QName(a).localname != "mtext":
            assert a.text == b.text, (a.get("id"), etree.QName(a).localname, a.text, b.text)
        if etree.QName(a).localname == "emphasis" and a.get("effect") == "italics" and re.fullmatch(r"[A-Za-z]", (a.text or "").strip()):
            assert a.text == b.text
    ns = {"c": CNX, "m": MATH}
    exercises = target.xpath("//c:exercise", namespaces=ns)
    solutions = target.xpath("//c:solution", namespaces=ns)
    media = target.xpath("//c:media", namespaces=ns)
    math = target.xpath("//*[namespace-uri()=$m]", m=MATH)
    assert len(exercises) == 116 and len(solutions) == 78 and len(media) == 68 and len(math) == 2011
    errata = json.loads(ERRATA.read_text(encoding="utf-8"))
    source_ids = {x.get("id") for x in se if x.get("id")}
    assert set(errata["entries"]).issubset(source_ids)
    numerical = run_math_checks(source, target)
    report = {
        "result": "pass",
        "module": "m82463",
        "source_sha256": sha(SRC),
        "translation_sha256": sha(GU),
        "errata_sha256": sha(ERRATA),
        "elements": len(ge),
        "source_ids": len(ids),
        "prose_slots": 351,
        "mathml_elements": len(math),
        "exercises": len(exercises),
        "source_solutions": len(solutions),
        "source_omitted_solutions": len(exercises) - len(solutions),
        "media": len(media),
        "translated_alt": sum(bool(x.get("alt")) for x in media),
        "translated_aria_labels": sum(bool(x.get("aria-label")) for x in ge),
        "translated_summaries": sum(bool(x.get("summary")) for x in ge),
        "translated_title_attributes": sum(bool(x.get("title")) for x in ge),
        "errata_entries": len(errata["entries"]),
        "numerical": numerical,
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "numerical"}, ensure_ascii=False, indent=2))
    print("Numerical exercises checked:", numerical["independently_recomputed"])


if __name__ == "__main__":
    main()
