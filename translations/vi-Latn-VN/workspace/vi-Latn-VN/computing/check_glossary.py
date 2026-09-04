"""Offline U017 source/transcription checks and finite logical illustrations.

Default needs only the committed excerpt and draft. --originals additionally
checks both existing pinned modules and the exact final-glossary boundary.
No downloads, generated files, image processing or continuous-graph proof.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
EXCERPT_SHA = "93a466839e6472a9c671abc322c000eeac73703a7969fd3786f1958c6c9b2b49"
ITEMS = (
    ("fs-id1165137758543", "fs-id1165137758548", "dependent variable",
     "Biến phụ thuộc", "Biến đầu ra."),
    ("fs-id1165137758552", "fs-id1165137932576", "domain",
     "Tập xác định", "Tập hợp tất cả các giá trị đầu vào có thể có của một quan hệ."),
    ("fs-id1165137932580", "fs-id1165137932585", "function",
     "Hàm số", "Quan hệ trong đó mỗi giá trị đầu vào tương ứng với đúng một giá trị đầu ra."),
    ("fs-id1165137932588", "fs-id1165134149777", "horizontal line test",
     "Kiểm tra bằng đường thẳng ngang",
     "Phương pháp kiểm tra một hàm số có đơn ánh hay không bằng cách xác định xem có đường thẳng ngang nào cắt đồ thị tại nhiều hơn một điểm hay không."),
    ("fs-id1165134149782", "fs-id1165134149787", "independent variable",
     "Biến độc lập", "Biến đầu vào."),
    ("fs-id1165135511353", "fs-id1165135511359", "input",
     "Đầu vào",
     "Mỗi đối tượng hoặc giá trị trong tập xác định được liên hệ với một đối tượng hoặc giá trị khác bởi một quan hệ gọi là hàm số."),
    ("fs-id1165135511364", "fs-id1165135511369", "one-to-one function",
     "Hàm số đơn ánh", "Hàm số mà mỗi giá trị đầu ra của nó tương ứng với đúng một giá trị đầu vào."),
    ("fs-id1165135508564", "fs-id1165135508569", "output",
     "Đầu ra",
     "Mỗi đối tượng hoặc giá trị trong tập giá trị được tạo ra khi một giá trị đầu vào được đưa vào hàm số."),
    ("fs-id1165135508573", "fs-id1165135315529", "range",
     "Tập giá trị",
     "Tập hợp các giá trị đầu ra tương ứng với các giá trị đầu vào trong một quan hệ."),
    ("fs-id1165135315533", "fs-id1165135315539", "relation",
     "Quan hệ", "Tập hợp các cặp có thứ tự."),
    ("fs-id1165135315542", "fs-id1165134186374", "vertical line test",
     "Kiểm tra bằng đường thẳng đứng",
     "Phương pháp kiểm tra một đồ thị có biểu diễn hàm số hay không bằng cách xác định xem mỗi đường thẳng đứng có cắt đồ thị tại nhiều nhất một điểm hay không."),
)


def relation_facts(pairs):
    """Domain/range are projections; injectivity requires a function first."""
    by_input, by_output = defaultdict(set), defaultdict(set)
    for x, y in set(pairs):
        by_input[x].add(y)
        by_output[y].add(x)
    is_function = all(len(values) == 1 for values in by_input.values())
    is_injective = is_function and all(len(values) == 1 for values in by_output.values())
    return set(by_input), set(by_output), is_function, is_injective


def total_on(pairs, declared_domain):
    domain, _, is_function, _ = relation_facts(pairs)
    return is_function and domain == set(declared_domain)


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, description, kind="structure"):
        assert condition, description
        counts[kind] += 1

    data = (ROOT / "sources/m49301-glossary-source.cnxml").read_bytes()
    source = ET.fromstring(data)
    md = (ROOT / "translation/A30-U017-glossary.vi.md").read_text("utf-8")
    explicit = re.findall(r"\{#([^}]+)\}", md)
    identities = [node.get("id") for node in source.iter() if node.get("id")]
    expected_ids = [identity for item in ITEMS for identity in item[:2]]
    check(sha256(data).hexdigest() == EXCERPT_SHA, "complete pinned glossary excerpt")
    check(md == unicodedata.normalize("NFC", md), "NFC Vietnamese")
    check(source.tag == f"{{{CN}}}glossary" and not source.get("id"), "exact unnumbered glossary")
    check(len(source) == 11, "eleven definitions")
    check(identities == expected_ids, "all twenty-two IDs in source order")
    check(len(explicit) == len(set(explicit)), "no duplicate explicit anchor")
    for identity in identities:
        check(explicit.count(identity) == 1, f"one source anchor {identity}")
    for tag, expected in (("definition", 11), ("term", 11), ("meaning", 11),
                          ("exercise", 0), ("solution", 0), ("image", 0),
                          ("table", 0), ("link", 0)):
        check(len(list(source.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")
    check(not list(source.iter(f"{{{MATH}}}math")), "no source MathML")
    check("{{math:" not in md, "no invented source MathML placeholders")

    translated_order = []
    for node, (definition, meaning, en_term, vi_term, vi_meaning) in zip(source, ITEMS):
        check([child.tag for child in node] == [f"{{{CN}}}term", f"{{{CN}}}meaning"],
              "definition retains term and meaning")
        check(node.get("id") == definition, "exact definition ID")
        check(node[1].get("id") == meaning, "exact meaning ID")
        check(node[0].text == en_term, "English source term unchanged")
        heading = f"### {vi_term} {{#{definition}}}"
        check(heading in md, f"consistent Vietnamese term: {vi_term}")
        translated_order.append(md.index(heading))
        match = re.search(r"::: \{#" + re.escape(meaning) + r"\}\s*\n(.*?)\n:::", md, re.S)
        check(match is not None, "meaning is a distinct source-ID block")
        check(" ".join(match.group(1).split()) == vi_meaning, "reviewed direct translation retained")
    check(translated_order == sorted(translated_order), "no Vietnamese-alphabetic resorting")
    check(md.count("*Làm rõ bổ sung:*") == 5, "five separate clarifications")
    check("*Hai ví dụ bổ sung — không phải ví dụ nguồn:*" in md, "two illustrations clearly new")
    check(not re.findall(r"\]\((?:#|A30-)", md), "no undeclared local or cross-reader links")
    check(not re.findall(r"!\[", md), "no source or new images")
    plain = " ".join(md.split())
    for phrase in (
        "Trước hết phải biết đồ thị biểu diễn một hàm số.",
        "Giá trị đầu ra” ở đây là giá trị thực sự đạt được",
        "mọi đường thẳng đứng, không chỉ một đường được chọn để thử",
        "Nếu tập xác định đã được cho riêng",
        "không được bỏ sót đầu vào",
        "ghi lặp lại cùng một cặp không tạo thêm phần tử mới",
        "không tự chứng minh rằng mọi nội dung trước đó đã được dịch",
    ):
        check(phrase in plain, f"material qualification: {phrase}")

    # These are finite illustrations of the definitions, not source exercises.
    cases = (
        ([(1, 2), (2, 2)], ({1, 2}, {2}, True, False)),
        ([(1, 2), (1, 3)], ({1}, {2, 3}, False, False)),
        ([(1, 2), (1, 2)], ({1}, {2}, True, True)),
        ([(1, 2), (2, 3)], ({1, 2}, {2, 3}, True, True)),
    )
    for pairs, expected in cases:
        actual = relation_facts(pairs)
        for index, label in enumerate(("domain", "range", "function", "injective")):
            check(actual[index] == expected[index], f"finite {label}: {pairs}", "finite")
    check(relation_facts([(2, 1), (2, 2)])[2:] == (False, False),
          "reversing ordered pairs can destroy functionhood", "finite")
    check(total_on([(1, 2)], {1}), "exactly one value at every declared input", "finite")
    check(not total_on([(1, 2)], {1, 2}), "missing declared input is not total", "finite")
    check(not total_on([(1, 2), (2, 3)], {1}), "extra input changes the stated domain", "finite")
    check(sum(x == 3 for x, _ in {(1, 2), (2, 2)}) == 0,
          "zero vertical intersections outside the domain are allowed", "finite")
    check(sum(y == 3 for _, y in {(1, 2), (2, 2)}) == 0,
          "zero horizontal intersections outside the range are allowed", "finite")
    check(relation_facts([(1, 2)])[3] and 3 not in relation_facts([(1, 2)])[1],
          "injectivity does not demand every value of a larger target set", "finite")
    check((1, 2) != (2, 1), "ordered pair order matters", "finite")

    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_glossary import ORIGINALS, extract, selected
        for relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest, "pinned original module", "original")
            original = selected(path)
            original_ids = [node.get("id") for node in original.iter() if node.get("id")]
            check(original_ids == identities, "EN/ID ordered glossary identities", "original")
            check(not list(original.iter(f"{{{MATH}}}math")), "EN/ID zero source MathML", "original")
            if "upstream-openstax" in relative:
                check(extract(path).encode("utf-8") == data, "complete final EN glossary reproduced", "original")
            else:
                last = original[-1].find(f"{{{CN}}}meaning").text
                check("setiap garis vertikal" in last, "ID explicitly requires every vertical line", "original")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv, details=True)
    print(f"PASS: {sum(result.values())} counted checks; {result}")
