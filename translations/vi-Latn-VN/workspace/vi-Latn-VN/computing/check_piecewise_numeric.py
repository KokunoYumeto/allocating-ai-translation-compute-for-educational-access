"""U028 exact evaluations, interval checks and source preservation; read-only.

Default uses only committed U028 files and Python's standard library.
--originals also checks the two pinned locally available source modules.
Finite branch/domain probes supplement, but do not replace, the written
set-union argument on every real input.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165134118450"
EXCERPT_SHA = "3545374212e7e21e9f6f72a4024052eb331a986d28e5ef223144a55cea13049b"
PROMPTS = ("fs-id1165135188383", "fs-id1165137469026", "fs-id1165137837869")
ITEMS = json.loads(r'''[{"number":46,"id":"fs-id1165137471865","problem_id":"fs-id1165137471867","prompt_id":"fs-id1165134043731","solution_id":null,"answer_id":null,"prompt_mn":["1","2","2","3","2"],"answer_mn":[]},{"number":47,"id":"fs-id1165134122954","problem_id":"fs-id1165134122956","prompt_id":"fs-id1165135168423","solution_id":"fs-id1165137804494","answer_id":"fs-id1165137804496","prompt_mn":["1","3","0","3"],"answer_mn":["3","1","2","0","1","0","0","0"]},{"number":48,"id":"fs-id1165137556768","problem_id":"fs-id1165137423742","prompt_id":"fs-id1165137423744","solution_id":null,"answer_id":null,"prompt_mn":["2","2","3","1","5","7","1"],"answer_mn":[]},{"number":49,"id":"fs-id1165134380351","problem_id":"fs-id1165134380353","prompt_id":"fs-id1165137678245","solution_id":"fs-id1165137476514","answer_id":"fs-id1165137476516","prompt_mn":["7","3","0","7","6","0"],"answer_mn":["1","4","0","6","2","20","4","34"]},{"number":50,"id":"fs-id1165137693713","problem_id":"fs-id1165137679373","prompt_id":"fs-id1165137679375","solution_id":null,"answer_id":null,"prompt_mn":["2","2","2","4","5","2"],"answer_mn":[]},{"number":51,"id":"fs-id1165137715004","problem_id":"fs-id1165137715006","prompt_id":"fs-id1165137715008","solution_id":"fs-id1165135699157","answer_id":"fs-id1165137401550","prompt_mn":["5","0","3","0","3","2","3"],"answer_mn":["1","5","0","3","2","3","4","16"]},{"number":52,"id":"fs-id1165137837872","problem_id":"fs-id1165135341427","prompt_id":"fs-id1165135341429","solution_id":null,"answer_id":null,"prompt_mn":["1","2","2","3","2"],"answer_mn":[]},{"number":53,"id":"fs-id1165137704661","problem_id":"fs-id1165137704664","prompt_id":"fs-id1165137704666","solution_id":"fs-id1165135420410","answer_id":"fs-id1165135570357","prompt_mn":["2","2","1","2","2","1"],"answer_mn":["1","1"]},{"number":54,"id":"fs-id1165137772429","problem_id":"fs-id1165137772431","prompt_id":"fs-id1165137675983","solution_id":null,"answer_id":null,"prompt_mn":["2","3","3","2","0","2"],"answer_mn":[]}]''')
MATH_TEXT = {"if": "nếu", "if\u00a0": "nếu\u00a0", "\u00a0if": "\u00a0nếu"}
EXPECTED = {
    46: (-2, 1, -1, -3), 47: (1, 0, 0, 0), 48: (-15, -5, 1, -7),
    49: (-4, 6, 20, 34), 50: (-1, -2, 7, 5), 51: (-5, 3, 3, 16),
}
INPUTS = {n: (-3, -2, -1, 0) if n < 49 else (-1, 0, 2, 4) for n in EXPECTED}
# Intervals: lower, upper, include_lower, include_upper. None is infinity.
ALL = ((None, None, False, False),)
DOMAINS = {
    52: ALL,
    53: ((None, F(1), False, False), (F(1), None, False, False)),
    54: ((None, F(0), False, False), (F(2), None, True, False)),
}


def branch_values(number, x):
    """All values admitted by the explicitly prescribed branch conditions."""
    choices = {
        46: ((x < -2, x+1), (x >= -2, -2*x-3)),
        47: ((x <= -3, F(1)), (x > -3, F(0))),
        48: ((x <= -1, -2*x*x+3), (x > -1, 5*x-7)),
        49: ((x < 0, 7*x+3), (x >= 0, 7*x+6)),
        50: ((x < 2, x*x-2), (x >= 2, 4+abs(x-5))),
        51: ((x < 0, 5*x), (0 <= x <= 3, F(3)), (x > 3, x*x)),
        52: ((x < -2, x+1), (x >= -2, -2*x-3)),
        53: ((x < 1, x*x-2), (x > 1, -x*x+2)),
        54: ((x < 0, 2*x-3), (x >= 2, -3*x*x)),
    }[number]
    return tuple(value for condition, value in choices if condition)


def in_intervals(x, intervals):
    return any((a is None or x > a or (lc and x == a))
               and (b is None or x < b or (rc and x == b))
               for a, b, lc, rc in intervals)


def merge_sorted_intervals(intervals):
    """Exact endpoint union for the already ordered branch-domain intervals."""
    output = []
    for a, b, lc, rc in intervals:
        if not output:
            output.append((a, b, lc, rc))
            continue
        p, q, pc, qc = output[-1]
        joins = q is None or a is None or a < q or (a == q and (lc or qc))
        if not joins:
            output.append((a, b, lc, rc))
        elif q is None or (b is not None and b < q):
            continue
        elif b == q:
            output[-1] = (p, q, pc, qc or rc)
        else:
            output[-1] = (p, b, pc, rc)
    return tuple(output)


def math_text(node):
    return (node.text or "").strip() + "".join(math_text(c) for c in node)


def answer_pairs(node):
    """Interpret the source's four equation cells, not its human prose."""
    row = next(node.iter(M+"mtr"))
    pairs = []
    for cell in row:
        match = re.fullmatch(r"f\(([−-]?\d+)\)=([−-]?\d+);?", math_text(cell))
        assert match, math_text(cell)
        pairs.append(tuple(F(v.replace("−", "-")) for v in match.groups()))
    return tuple(pairs)


def parse_intervals(node):
    intervals = []
    for part in math_text(node).split("∪"):
        match = re.fullmatch(r"([\(\[])([^,]+),([^,\]\)]+)([\)\]])", part)
        assert match, part
        left, a, b, right = match.groups()
        convert = lambda value: None if "∞" in value else F(value.replace("−", "-"))
        intervals.append((convert(a), convert(b), left == "[", right == "]"))
    return tuple(intervals)


def math_signature(node):
    text = node.text or ""
    if node.tag == M+"mtext":
        text = {"jika": "if", "jika\u00a0": "if\u00a0", "\u00a0jika": "\u00a0if"}.get(text, text)
    else:
        text = text.strip()
    return (node.tag, tuple(sorted(node.attrib.items())), text,
            tuple((math_signature(c), (c.tail or "").strip()) for c in node))


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, message, kind="source_structure"):
        assert condition, message
        counts[kind] += 1

    data = (ROOT/"sources/m49304-piecewise-numeric-source.cnxml").read_bytes()
    source = ET.fromstring(data)
    md = (ROOT/"translation/A30-U028-piecewise-numeric.vi.md").read_text("utf-8")
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", md)
    check(sha256(data).hexdigest() == EXCERPT_SHA, "exact full Numeric excerpt")
    check(md == unicodedata.normalize("NFC", md), "Vietnamese NFC")
    check(len(by_id) == 39, "39 module-qualified source identities")
    check(len(anchors) == len(set(anchors)), "no duplicate explicit anchors")
    for identity in by_id:
        check(anchors.count(identity) == 1, f"source anchor once:m49304/{identity}")
    for tag, expected in (("section",1), ("exercise",9), ("problem",9), ("solution",4),
                          ("image",0), ("figure",0), ("example",0), ("list",0)):
        check(len(list(source.iter(CN+tag))) == expected, f"source {tag}:{expected}")
    section = by_id[SECTION]
    check([n.get("id") for n in section if n.tag == CN+"para"] == list(PROMPTS),
          "three shared instructions in order")
    check([n.get("id") for n in source.iter(CN+"exercise")] == [i["id"] for i in ITEMS],
          "nine exercises in original order")
    check(re.findall(r"^### Bài (\d+) ", md, re.M) == [str(n) for n in range(46,55)],
          "continuous original numbering46–54")
    check(re.findall(r"^### Lời giải Bài (\d+) ", md, re.M) == [str(n) for n in range(46,55)],
          "nine answer sections in matching order")
    check("fs-id1165137580833" not in anchors and "fs-id1165135194497" not in anchors,
          "neighbor category IDs outside this unit")
    maths = list(source.iter(M+"math"))
    check(len(maths) == 19, "19 source MathML expressions")
    captures = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", md):
        check(identity in by_id, "source MathML owner exists")
        options = list(by_id[identity].iter(M+"math"))
        check(int(index) < len(options), "valid local MathML index")
        captures.append(options[int(index)])
    check(Counter(map(id,captures)) == Counter(map(id,maths)), "all19 source maths once")
    check(Counter(n.text for n in source.iter(M+"mtext")) ==
          Counter({"if":13,"if\u00a0":4,"\u00a0if":2}), "19 exact padded if payloads")
    for node in source.iter(M+"mtext"):
        check(node.text in MATH_TEXT, "each source mtext has an exact Vietnamese mapping")
    check(md.count("**Đáp án nguồn:**") == 4, "four source answers labeled")
    check(md.count("**Lời giải bổ sung — nguồn không kèm đáp án:**") == 5,
          "five newly authored answers labeled")
    check(md.count("*Giải thích bổ sung:*") == 4, "new explanations separated from source answers")
    for prompt, inputs in ((PROMPTS[0], ["−3","−2","−1","0"]),
                           (PROMPTS[1], ["−1","0","2","4"])):
        check([n.text for n in by_id[prompt].iter(M+"mn")] == inputs,
              "all four inputs retained in shared instruction")
        check(len(list(by_id[prompt].iter(M+"math"))) == 3, "shared instruction has three maths")
    for item in ITEMS:
        number = item["number"]
        ex = by_id[item["id"]]
        check(ex.find(CN+"problem").get("id") == item["problem_id"],
              f"source problem identity:{number}")
        check([n.text for n in by_id[item["prompt_id"]].iter(M+"mn")] == item["prompt_mn"],
              f"source prompt numerals:{number}")
        solutions = list(ex.iter(CN+"solution"))
        check([n.get("id") for n in solutions] ==
              ([item["solution_id"]] if item["solution_id"] else []),
              f"source answer presence:{number}")
        target = item["solution_id"] or f"vi-sol-{number}"
        check(f"[Lời giải Bài {number}](#{target})" in md, f"answer jump:{number}")
        check(f"[Trở lại Bài {number}](#{item['id']})" in md, f"backlink:{number}")
        if item["answer_id"]:
            answer = by_id[item["answer_id"]]
            check([n.text for n in answer.iter(M+"mn")] == item["answer_mn"],
                  f"source answer numerals:{number}")
            if number < 52:
                check(answer_pairs(answer) == tuple(zip(INPUTS[number], EXPECTED[number])),
                      f"all four supplied results interpreted:{number}", "exact_math")
            else:
                check(parse_intervals(next(answer.iter(M+"math"))) == DOMAINS[number],
                      "source Bài53 interval interpreted", "exact_math")
        if number in EXPECTED:
            for x, expected in zip(INPUTS[number], EXPECTED[number]):
                check(branch_values(number,F(x)) == (F(expected),),
                      f"required evaluation:{number}:f({x})={expected}", "exact_math")
        else:
            for x in map(F,("-100","-2.1","-2","-1.9","-0.1","0","0.1","0.9",
                             "1","1.1","1.9","2","2.1","100")):
                actual = branch_values(number,x)
                check(len(actual) <= 1 and bool(actual) == in_intervals(x,DOMAINS[number]),
                      f"finite domain witness:{number}:{x}", "finite_domain")
    local = re.findall(r"\]\(#([^)]*)\)", md)
    check(len(local) == 18 and all(anchors.count(t)==1 for t in local), "all18 local links resolve")
    check(not re.findall(r"\]\(A30-",md), "zero cross-reader links")
    check("![" not in md, "no image needed or introduced")
    plain = " ".join(md.split())
    for phrase in ("hợp các tập đầu vào hợp lệ", "đồng thời thỏa điều kiện",
                   "không cho phép bỏ những giới hạn", "thay biến bằng đầu vào",
                   "Không chọn nhánh chỉ vì", "Hệ số $-2$ vẫn ở ngoài bình phương",
                   "không nhánh nào nhận $x=1$", "Không đầu vào nào thuộc $[0,2)$",
                   "Một số đầu vào thử không thay thế lập luận"):
        check(phrase in plain, f"mathematical qualification:{phrase}")
    for number, expected in ((46,r"f(-3)=-3+1=-2"), (46,r"f(-2)=-2(-2)-3=1"),
                             (46,r"f(-1)=-2(-1)-3=-1"), (46,r"f(0)=-2\cdot0-3=-3"),
                             (48,r"f(-3)=-2(-3)^2+3=-18+3=-15"),
                             (48,r"f(-2)=-2(-2)^2+3=-8+3=-5"),
                             (48,r"f(-1)=-2(-1)^2+3=-2+3=1"), (48,r"f(0)=5\cdot0-7=-7"),
                             (50,r"f(-1)=(-1)^2-2=-1"), (50,r"f(0)=0^2-2=-2"),
                             (50,r"f(2)=4+|2-5|=4+3=7"), (50,r"f(4)=4+|4-5|=4+1=5"),
                             (52,r"(-\infty,-2)\cup[-2,\infty)=(-\infty,\infty)"),
                             (54,r"(-\infty,0)\cup[2,\infty)")):
        start = md.index(f"### Lời giải Bài {number} ")
        end = md.index(f"[Trở lại Bài {number}]",start)
        check(expected in md[start:end], f"reviewed new result present:{number}:{expected}")
    # Full interval endpoint unions are exact set operations, not sampled inputs.
    branch_intervals = {
        52: ((None,F(-2),False,False),(F(-2),None,True,False)),
        53: ((None,F(1),False,False),(F(1),None,False,False)),
        54: ((None,F(0),False,False),(F(2),None,True,False)),
    }
    for number, intervals in branch_intervals.items():
        check(merge_sorted_intervals(intervals) == DOMAINS[number],
              f"exact union of prescribed branch intervals:{number}", "exact_math")
    for number, x, expected in ((46,-2,1),(47,-3,1),(48,-1,1),(49,0,6),
                               (50,2,7),(51,0,3),(51,3,3),(54,2,-12)):
        check(branch_values(number,F(x)) == (F(expected),),
              f"closed-boundary assigned branch:{number}:{x}", "exact_math")
    check(branch_values(53,F(1)) == (), "Bài53 no branch at1", "exact_math")
    check(branch_values(54,F(0)) == (), "Bài54 no branch at0", "exact_math")
    tables = list(by_id["fs-id1165137675983"].iter(M+"mtable"))
    check(len(tables)==2 and [len(t) for t in tables]==[2,2],
          "Bài54 separate source expression/condition tables kept")
    check([math_text(r) for r in tables[1]] == ["ifx<0","ifx≥2"],
          "Bài54 second branch starts at2, not0")
    check([math_text(r) for r in tables[0]] == ["2x−3","−3x2"],
          "Bài54 polynomial rows retain source order")

    if originals:
        sys.path.insert(0,str(ROOT/"tools"))
        from extract_piecewise_numeric import ORIGINALS, extract
        for relative,digest in ORIGINALS:
            path = ROOT.parent/relative
            check(sha256(path.read_bytes()).hexdigest()==digest, "pinned original", "originals")
            reproduced = extract(path)
            original = ET.fromstring(reproduced)
            check([n.get("id") for n in original.iter() if n.get("id")]==list(by_id),
                  "all39 EN/ID ordered source identities", "originals")
            check([math_signature(n) for n in original.iter(M+"math")] ==
                  [math_signature(n) for n in maths],
                  "all19 original maths identical apart from exact if/jika payloads", "originals")
            check([n.get("id") for n in original.iter(CN+"solution")] ==
                  [i["solution_id"] for i in ITEMS if i["solution_id"]],
                  "four identical EN/ID source answer slots", "originals")
            if "upstream-openstax" in relative:
                check(reproduced.encode("utf-8")==data, "complete exact EN subtree reproduced", "originals")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv,details=True)
    print(f"PASS: {sum(result.values())} mixed assertions; {result}; finite probes are not proofs")
