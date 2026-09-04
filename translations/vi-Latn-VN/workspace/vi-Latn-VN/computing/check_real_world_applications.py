"""U016 standalone source/units/notation and exact finite arithmetic checks.

Default uses only committed draft/excerpt and Python stdlib. --originals also
compares the existing pinned full EN/ID modules and the final-content boundary.
These checks do not validate empirical garbage/garden/duck/rocket models.
One exact collision is a proof against injectivity, not evidence for injectivity.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
EXCERPT_SHA = "c1dfda77c9792efab15c9a279ba4ecb12632c0f7c14fb005c7632013c624bdb2"
EXERCISES = [
    "fs-id1165135580355", "fs-id1165137922382", "fs-id1165135553615",
    "fs-id1165134272734", "fs-id1165135708043",
]
SOLUTIONS = [None, "fs-id1165135434096", None, "fs-id1165135708034", None]


def notation(node):
    tag = node.tag.rsplit("}", 1)[-1]
    if tag in ("mi", "mn", "mo"):
        return (node.text or "").strip()
    if tag == "msup":
        return f"({notation(node[0])})^({notation(node[1])})"
    if tag not in ("math", "mrow"):
        raise ValueError(f"Unexpected MathML tag: {tag}")
    return "".join(map(notation, node))


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, description, kind="structure"):
        assert condition, description
        counts[kind] += 1

    data = (ROOT / "sources/m49301-real-world-applications-source.cnxml").read_bytes()
    tree = ET.fromstring(data)
    md = (ROOT / "translation/A30-U016-real-world-applications.vi.md").read_text("utf-8")
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned selected excerpt bytes")
    check(tree.get("id") == "fs-id1165135580349", "complete Real-World parent retained")
    check(tree[0].tag == f"{{{CN}}}title" and tree[0].text == " Real-World Applications",
          "source title retained including leading space")
    check(md == unicodedata.normalize("NFC", md), "NFC Vietnamese")
    ordered_ids = [n.get("id") for n in tree.iter() if n.get("id")]
    ids = {n.get("id"): n for n in tree.iter() if n.get("id")}
    check(len(ordered_ids) == len(ids) == 24, "24 unique source IDs")
    explicit = re.findall(r"\{#([^}]+)\}", md)
    check(len(explicit) == len(set(explicit)), "all authored anchors unique")
    for identity in ids:
        check(explicit.count(identity) == 1, f"one explicit source ID {identity}")
    for tag, expected in (("exercise", 5), ("problem", 5), ("solution", 2),
                          ("para", 5), ("list", 6), ("item", 12), ("image", 0),
                          ("table", 0), ("link", 0)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")
    check([n.get("id") for n in tree.findall(f"{{{CN}}}exercise")] == EXERCISES,
          "five exercise order88-92")
    for number, identity, solution in zip(range(88, 93), EXERCISES, SOLUTIONS):
        check(f"### Bài {number} {{#{identity}}}" in md, "source-wide numbering")
        actual = ids[identity].find(f"{{{CN}}}solution")
        check((actual.get("id") if actual is not None else None) == solution,
              "source/new solution inventory")
        label = "Lời giải nguồn" if solution else "Lời giải bổ sung"
        check(f"### Bài {number} — {label}" in md, "accurate solution labeling")
    check(md.count("Nguồn không kèm lời giải cho") == 3, "three new-solution disclosures")
    links = re.findall(r"\]\(#([^)]+)\)", md)
    check(len(links) == 5, "five answer links")
    for target in links:
        check(target in explicit, f"valid local answer link {target}")
    check(re.findall(r"\]\((?!#)([^)]+)\)", md) == [
        "https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768",
        "https://github.com/KokunoYumeto/openstax-precalculus-2e-id",
        "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    ] and "{#vi-attribution}" in md and "Copyright Rice University, OpenStax" in md,
          "three unfetched attribution URLs and local component credit, no cross-reader dependency")

    source_math = list(tree.iter(f"{{{M}}}math"))
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", md):
        inserted.append(list(ids[identity].iter(f"{{{M}}}math"))[int(index)])
    check(len(source_math) == len(inserted) == 22, "22 source math occurrences")
    check(Counter(map(id, source_math)) == Counter(map(id, inserted)), "every source math once")
    check(not list(tree.iter(f"{{{M}}}mtext")), "no MathML text dictionary needed")
    expected_notations = {
        "fs-id1165135580359": ["G,", "p", "G=f(p).", "G", "p"],
        "fs-id1165135380706": ["f.", "f(5)=2."],
        "fs-id1165134269007": ["D,", "a", "D=g(a)."],
        "fs-id1165137834372": ["g.", "g(100)=1."],
        "eip-idm959115456": ["g(5000)=50;"],
        "fs-id1165135553620": ["f(t)", "t"],
        "fs-id1165135186507": ["f(5)=30", "f(10)=40"],
        "fs-id1165134272739": ["h(t)", "t"],
        "fs-id1165135342160": ["h(1)=200", "h(2)=350"],
        "fs-id1165137844421": ["f(x)=3((x−5))^(2)+7"],
    }
    for identity, expected in expected_notations.items():
        check([notation(n) for n in ids[identity].iter(f"{{{M}}}math")] == expected,
              f"independent complete source notation transcription {identity}")

    # Preserve dimensional distinctions and part labels without metric conversions.
    source_prose = lambda identity: " ".join("".join(ids[identity].itertext()).split())
    for identity, phrases in {
        "fs-id1165135580359": ["tons per week", "thousands of people"],
        "fs-id1165135380706": ["40,000", "13 tons"],
        "fs-id1165134269007": ["cubic yards", "square feet"],
        "fs-id1165137834372": ["5000 ft2", "50 yd3"],
        "fs-id1165135553620": ["years after 1990"],
        "fs-id1165134272739": ["height above ground, in feet", "seconds after launching"],
        "eip-idm959115456": ["100 square feet is 1"],
        "eip-idm528575840": ["after 1 second is 200 ft", "after 2 seconds is 350 ft"],
    }.items():
        for phrase in phrases:
            check(phrase in source_prose(identity), f"source unit/data {phrase}", "units")
    for identity in ("fs-id1165135380706", "fs-id1165137834372",
                     "fs-id1165135186507", "fs-id1165135342160",
                     "eip-idm959115456", "eip-idm528575840"):
        listed = ids[identity]
        check(listed.get("class") == "circled" and len(listed) == 2, "two-part circled source list")
        block = md.split(f"{{#{identity}}}", 1)[1].split(":::", 1)[0]
        check(block.count("ⓐ") == block.count("ⓑ") == 1, "both translated part labels")
    rocket_list = ids["fs-id1165135342160"]
    check(not list(rocket_list.iter(f"{{{CN}}}span")),
          "rocket problem has implied list labels, not explicit source span tokens")
    emphasis = ids["fs-id1165137844421"].find(f"{{{CN}}}emphasis")
    check(emphasis.get("effect") == "underline" and emphasis.text == "not", "source negation emphasis")
    check("<u>không</u> đơn ánh" in md, "translated negation and underline retained")

    # Exact finite requested values. Input scaling belongs only to exercise88.
    for actual, expected, label in (
        (Fraction(40000, 1000), 40, "garbage input in thousands"),
        (5 * 1000, 5000, "garbage population from input5"),
        (1990 + 5, 1995, "duck year for input5"),
        (1990 + 10, 2000, "duck year for input10"),
    ):
        check(actual == expected, label, "arithmetic")
    for identity, expected in (
        ("fs-id1165135380706", ["5", "2."]),
        ("fs-id1165137834372", ["100", "1."]),
        ("eip-idm959115456", ["5000", "50"]),
        ("fs-id1165135186507", ["5", "30", "10", "40"]),
        ("fs-id1165135342160", ["1", "200", "2", "350"]),
        ("fs-id1165137844421", ["3", "5", "2", "7"]),
    ):
        check([n.text for n in ids[identity].iter(f"{{{M}}}mn")] == expected,
              "source mathematical numeric input/output sequence", "units")
    f = lambda x: 3*(x-5)**2 + 7
    check(f(4) == 10, "exact f4", "arithmetic")
    check(f(6) == 10, "exact f6", "arithmetic")
    check(4 != 6 and f(4) == f(6), "exact distinct-input collision refutes injectivity", "arithmetic")
    for text in (
        r"p=\frac{40\,000}{1000}=40", "f(40)=13",
        r"$5\times1000=5000$", "2 ton rác mỗi tuần",
        "$1990+5=1995$", "30 con vịt", "$1990+10=2000$", "40 con vịt",
        "100 foot vuông cần 1 yard khối", "5000 ft² cần 50 yd³",
        "1 giây, tên lửa ở độ cao 200 ft", "2 giây, tên lửa ở độ cao 350 ft",
        r"f(4)=3(4-5)^2+7=10", r"f(6)=3(6-5)^2+7=10",
        r"$4\ne6$", r"tự nhiên $\mathbb{R}$", "không phải vận tốc",
        "không mặc nhiên đồng nhất đơn vị ấy với tấn hệ mét",
        "không dùng đơn vị nghìn foot vuông", "không phải số vịt tăng thêm",
        "chỉ cần một cặp như vậy là đủ", "không xác nhận",
    ):
        check(text in md, f"authored answer/unit/domain qualification retained: {text}")
    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_real_world_applications import ORIGINALS, selected, math_serials
        for relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest, "pinned full source", "original")
            original = selected(path)
            check([n.get("id") for n in original.iter() if n.get("id")] == ordered_ids,
                  "EN/ID complete ordered category IDs and exact boundary", "original")
            check(math_serials(original) == math_serials(tree), "all EN/ID source MathML", "original")
            if "upstream-openstax" in relative:
                # Section tail is parent-level whitespace, outside the selected
                # subtree; reparsing a standalone XML root does not retain it.
                original.tail = None
                check(ET.tostring(original) == ET.tostring(tree), "exact selected EN subtree", "original")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv, details=True)
    print(f"PASS: {sum(result.values())} assertions; {result}")
