"""U024 source preservation and finite root/domain/endpoint witnesses.

No graph files or readers are built. Samples do not prove claims over all reals.
The two empty mroot index rows are meaningful source structure and are retained.
"""
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isfinite, sqrt
from pathlib import Path
import argparse
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
EXCERPT_SHA = "e52f46484105ee721ab3c8d1a6f797e2840649f7a986c650a511f5e1baa6f45b"
DRAFT_SHA = "9f6775068c2c9899c9c5698dca8ad922df43a80222d6f02645e919a6298a2b21"
EN_SHA = "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"
ID_SHA = "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"
EXERCISES = ["fs-id1165137665109", "fs-id1165135440209", "fs-id1165137635386",
             "fs-id1165134042454", "fs-id1165134211324"]
SOLUTIONS = ["fs-id1165134199600", "fs-id1165137727146", "fs-id1165137574335"]
MATH_KEYS = [
    ("fs-id1165135390942", 0), ("fs-id1165135390942", 1),
    ("fs-id1165137727148", 0), ("fs-id1165137727148", 1),
    ("fs-id1165137727148", 2), ("fs-id1165137727148", 3),
    ("fs-id1165137727148", 4), ("fs-id1165137727148", 5),
    ("fs-id1165135415726", 0), ("fs-id1165135415726", 1),
    ("fs-id1165135415726", 2), ("fs-id1165135415726", 3),
]


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def interval_contains(x, a, b, left_closed, right_closed):
    return (a <= x if left_closed else a < x) and (x <= b if right_closed else x < b)


def tests(originals=False):
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    excerpt_path = ROOT / "sources/m49304-domain-verbal-source.cnxml"
    draft_path = ROOT / "translation/A30-U024-domain-verbal.vi.md"
    extractor_path = ROOT / "tools/extract_domain_verbal.py"
    checker_path = Path(__file__).resolve()
    canon_path = ROOT / "canon/review-A30-U024.json"
    provenance_path = ROOT / "provenance/U024-source-review.json"
    data = excerpt_path.read_bytes()
    canon_data = canon_path.read_bytes()
    canon = json.loads(canon_data)
    provenance = json.loads(provenance_path.read_bytes())
    check(
        sha256(data).hexdigest() == EXCERPT_SHA
        and provenance["source_excerpt_sha256"] == EXCERPT_SHA
        and canon["source_excerpt_sha256"] == EXCERPT_SHA
        and provenance["extraction_script_sha256"] == sha256(extractor_path.read_bytes()).hexdigest()
        and provenance["computing_check_sha256"] == sha256(checker_path.read_bytes()).hexdigest()
        and provenance["canon_review_sha256"] == sha256(canon_data).hexdigest(),
        "exact excerpt, extractor, checker and canon bindings",
    )
    source = ET.fromstring(data)
    draft_data = draft_path.read_bytes()
    draft = draft_data.decode("utf-8")
    check(
        draft == unicodedata.normalize("NFC", draft)
        and sha256(draft_data).hexdigest() == DRAFT_SHA
        and provenance["translation_sha256"] == DRAFT_SHA
        and canon["translation_sha256"] == DRAFT_SHA,
        "Vietnamese NFC and exact draft bindings",
    )
    ids = [n.get("id") for n in source.iter() if n.get("id")]
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(ids) == len(set(ids)) == 23, "23 module-local source IDs")
    check(all(n == 1 for n in Counter(anchors).values()) and
          [anchor for anchor in anchors if anchor in by_id] == ids,
          "unique draft anchors and exact source-anchor order")
    for identity in ids:
        check(anchors.count(identity) == 1, f"retained source ID {identity}")
    check([n.get("id") for n in source.iter(CN + "section")] ==
          ["fs-id1165135176628", "fs-id1165135172218"], "outer heading plus complete Verbal category")
    check(list(by_id["fs-id1165135176628"])[0].text == "Section Exercises", "original outer heading")
    check("fs-id1165137771069" not in ids, "Algebraic stop excluded")
    check([n.get("id") for n in source.iter(CN + "exercise")] == EXERCISES, "all five original exercises in order")
    check([n.get("id") for n in source.iter(CN + "solution")] == SOLUTIONS, "three actual source answers")
    check([n for n in EXERCISES if by_id[n].find(CN + "solution") is None] ==
          [EXERCISES[1], EXERCISES[3]], "only Bài2 and Bài4 have new answers")
    blocks = re.findall(r"#### Bài (\d+).*?(?=\n#### Bài |\n## Tự kiểm tra)", draft, re.S)
    bodies = re.findall(r"#### Bài \d+.*?(?=\n#### Bài |\n## Tự kiểm tra)", draft, re.S)
    labels = [(number, body.count("**Lời giải nguồn.**"),
               body.count("**Lời giải bổ sung — nguồn không kèm đáp án.**"))
              for number, body in zip(blocks, bodies)]
    check(labels == [("1", 1, 0), ("2", 0, 1), ("3", 1, 0),
                     ("4", 0, 1), ("5", 1, 0)],
          "source and supplemental answer labels belong to the correct exercises")
    check(sum(source_count for _, source_count, _ in labels) == 3 and
          sum(new_count for _, _, new_count in labels) == 2,
          "exactly three source and two supplemental answers")
    check(re.findall(r"#### Bài (\d+)", draft) == ["1", "2", "3", "4", "5"], "continuous exercise numbering")
    check(not list(source.iter(CN + "image")) and "![" not in draft, "no source or added images")
    check(not list(source.iter(CN + "link")), "no original exercise crossreferences")
    check(not re.findall(r"\]\(A30-", draft), "no cross-reader dependency")
    math = list(source.iter(M + "math"))
    refs = [(identity, int(index)) for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)]
    check(refs == MATH_KEYS, "all twelve exact source math references in reader order")
    captured = [list(by_id[identity].iter(M + "math"))[index] for identity, index in refs]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "all12MathML once without omission/duplication")
    check(len(math) == 12 and not list(source.iter(M + "mtext")), "12MathML and no prose mtext")
    roots = list(source.iter(M + "mroot"))
    check(len(roots) == 4, "four source radical occurrences")
    check([list(n)[1].tag for n in roots] == [M + "mn", M + "mrow", M + "mn", M + "mrow"],
          "cube roots and empty-index square roots in source order")
    for root in (roots[1], roots[3]):
        index = list(root)[1]
        check(len(root) == 2 and len(index) == 0 and not (index.text or "").strip(),
              "source empty square-root index retained, not pruned")
    check([n.text for n in by_id["fs-id1165135390942"].iter(M + "mn")] == ["3"], "prompt root index")
    check([n.text for n in by_id["fs-id1165137727148"].iter(M + "mn")] == ["3", "0"], "answer index and endpoint")
    flat_draft = " ".join(draft.split())
    for phrase in ("tập xác định thực lớn nhất", "đã quy định tập xác định", "imaginary",
                   "giá trị không thực", "đồng thời", "Chẳng hạn, mẫu số", "căn chính không âm",
                   "ngoặc tròn", "ngoặc vuông", "không phải số thực", "giữa các đồ thị thành phần",
                   "không bắt buộc", "cùng giá trị", "Kiểm tra hữu hạn"):
        check(phrase in flat_draft, f"meaning/qualification {phrase}")

    #50 finite mathematical witnesses, not proofs over infinite domains.
    math_start = count
    for y, x in ((-3, -27), (-2, -8), (-1, -1), (0, 0), (1, 1), (2, 8), (3, 27)):
        check(y ** 3 == x, "real cube-root witness")
    for x, allowed in ((-4, False), (-1, False), (0, True), (1, True), (4, True), (9, True)):
        check((x >= 0) == allowed, "real square-root domain sample")
    check(sqrt(9) == 3, "principal square root")
    for y in (-3, 3):
        check(y * y == 9, "equation root, not both function values")
    check(sqrt(9) != -3, "negative equation root not principal square root")
    for x, allowed in ((-1, True), (0, True), (1, False), (2, True)):
        check((x - 1 != 0) == allowed, "denominator restriction before cancellation")
    for x, allowed in ((1, False), (2, False), (3, True), (6, True)):
        check((x - 2 >= 0 and x - 2 != 0) == allowed, "even root in denominator combines restrictions")
    for left, right in ((False, False), (True, True), (False, True), (True, False)):
        for x in (-2, -1, 0, 2, 3):
            expected = x == 0 or (x == -1 and left) or (x == 2 and right)
            check(interval_contains(x, -1, 2, left, right) == expected, "finite interval endpoint convention")
    for x, allowed in ((0, True), (1, True), (5, True), (float("inf"), False)):
        check((isfinite(x) and x >= 0) == allowed, "unbounded interval has only real elements")
    check(0 == 2 * 0, "compatible singleton branch overlap")
    assert count - math_start == 50

    spec = spec_from_file_location("u024_extract", extractor_path)
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    if originals:
        for language, path, expected_sha in (
            ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml", EN_SHA),
            ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml", ID_SHA),
        ):
            if not path.is_file():
                raise AssertionError(f"required {language} original is unavailable: {path}")
            selected = ET.fromstring(extractor.extract(path))
            check(sha256(path.read_bytes()).hexdigest() == expected_sha and
                  provenance["source_module_sha256"][language] == expected_sha and
                  [n.get("id") for n in selected.iter() if n.get("id")] == ids,
                  f"pinned full-file hash and all source IDs {language}")
            check([canonical(n) for n in selected.iter(M + "math")] ==
                  [canonical(n) for n in math], f"all original MathML exactly agrees {language}")
            check([n.get("id") for n in selected.iter(CN + "solution")] == SOLUTIONS, f"answer presence {language}")
            if language == "en":
                check(extractor.extract(path) == data.decode("utf-8"), "exact reproducible English excerpt")
                check(canonical(selected) == canonical(source), "all original English content")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", action="store_true",
                        help="require and compare the pinned full EN and Indonesian modules")
    args = parser.parse_args()
    print(f"PASS: {tests(args.originals)} mixed source/structure and finite mathematical assertions "
          f"(50 mathematical witnesses; originals={'required' if args.originals else 'not requested'})")
