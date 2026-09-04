"""Prepare source-bound slots and paired reading records for A10 m82463."""
from pathlib import Path
import hashlib
import json
import re
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REVIEWS = HERE.parent / "reviews"
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82463/index.cnxml"
INDO = ROOT / "downloads/gu-Gujr-IN/a10-release/source/translated/modules/m82463/index.cnxml"
MAP = HERE / "a10-m82463.slots.json"
PROSE = REVIEWS / "a10-m82463-paired-prose.json"
EXERCISES = REVIEWS / "a10-m82463-paired-exercises.json"
SOURCE_SHA = "b6345a5a6a99108f9d32d6518445a4ae70a6b0c54a258021dffc6f2b77b8278a"
INDO_SHA = "0f9d709ce2b32c18254be9f11a57db1b70f9477739e2b9dddc6857ad3992fe85"
MATH = "http://www.w3.org/1998/Math/MathML"
CNX = "http://cnx.rice.edu/cnxml"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def values(elem):
    local = etree.QName(elem).localname
    namespace = etree.QName(elem).namespace
    if local not in {"content-id", "uuid"}:
        for attr in ("text", "tail"):
            value = getattr(elem, attr)
            if value and re.search(r"[A-Za-z]", value) and not (
                namespace == MATH and attr == "text" and local != "mtext"
            ):
                yield attr, value.strip()
        for attr in ("alt", "summary", "aria-label", "title"):
            value = elem.get(attr)
            if value and re.search(r"[A-Za-z]", value):
                yield "@" + attr, value.strip()


def owner_id(elem):
    cursor = elem
    while cursor is not None:
        if cursor.get("id"):
            return cursor.get("id")
        cursor = cursor.getparent()
    return None


def flat(elem):
    return " ".join(" ".join(elem.itertext()).split())


def main():
    assert sha(SRC) == SOURCE_SHA and sha(INDO) == INDO_SHA
    source = etree.parse(str(SRC)).getroot()
    indo = etree.parse(str(INDO)).getroot()
    se = list(source.iter())
    ie = list(indo.iter())
    assert len(se) == len(ie) == 3249
    assert [(etree.QName(x).namespace, etree.QName(x).localname) for x in se] == [
        (etree.QName(x).namespace, etree.QName(x).localname) for x in ie
    ]
    rows = []
    by_en = {}
    for index, (a, b) in enumerate(zip(se, ie)):
        bv = dict(values(b))
        for attr, en in values(a):
            indo_value = bv.get(attr, "")
            if en not in by_en:
                row = {
                    "n": len(rows),
                    "en": en,
                    "indo": indo_value,
                    "owner": owner_id(a),
                    "element": etree.QName(a).localname,
                    "field": attr,
                    "occurrences": 1,
                    "element_index": index,
                }
                rows.append(row)
                by_en[en] = row
            else:
                by_en[en]["occurrences"] += 1
    MAP.write_text(
        json.dumps(
            {"source_sha256": SOURCE_SHA, "indonesian_sha256": INDO_SHA, "slots": rows},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    prose = []
    for index, (a, b) in enumerate(zip(se, ie)):
        local = etree.QName(a).localname
        if local in {"para", "title", "caption", "note", "definition"}:
            prose.append(
                {"element_index": index, "element": local, "id": owner_id(a), "source": flat(a), "indonesian": flat(b)}
            )
    PROSE.write_text(json.dumps(prose, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    source_ex = [x for x in se if etree.QName(x).localname == "exercise"]
    indo_ex = [x for x in ie if etree.QName(x).localname == "exercise"]
    assert len(source_ex) == len(indo_ex) == 116
    exercise_rows = []
    for number, (a, b) in enumerate(zip(source_ex, indo_ex), 1):
        ssol = [x for x in a.iter() if etree.QName(x).localname == "solution"]
        isol = [x for x in b.iter() if etree.QName(x).localname == "solution"]
        assert len(ssol) == len(isol)
        exercise_rows.append(
            {
                "number": number,
                "source_exercise": a.get("id"),
                "source": flat(a),
                "indonesian": flat(b),
                "source_solution_count": len(ssol),
                "source_solutions": [flat(x) for x in ssol],
                "indonesian_solutions": [flat(x) for x in isol],
            }
        )
    EXERCISES.write_text(json.dumps(exercise_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(rows)} slots, {len(prose)} prose records, {len(exercise_rows)} exercises")


if __name__ == "__main__":
    main()
