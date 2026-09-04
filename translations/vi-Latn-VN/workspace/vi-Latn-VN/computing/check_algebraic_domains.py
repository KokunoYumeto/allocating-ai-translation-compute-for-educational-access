"""U025 source preservation and exact rational/algebra checks; read-only.

Default needs only committed U025 files and the Python standard library.
--originals additionally requires both pinned local originals.
The separate plot generator --check additionally needs Pillow and the
recorded Unicode font. Finite input tests are not infinite-domain proofs.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import re
import struct
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137771069"
EXCERPT_SHA = "a3b95e73b9b6c0eaa0f8b38e557d419985676418a9e2c236663c2ef33467155d"
DRAFT_SHA = "d54c4975b9074d657c9182b6b6f645c70278e28627cbd500ad9d7a975fc74441"
PNG_SHA = "0413bca750438365146fe10e5c10daf36bf5818013f43521fa4eb9723fe663a6"

ITEMS = json.loads(r'''[{"number":6,"id":"fs-id1165137833819","problem_id":"fs-id1165137833821","prompt_id":"fs-id1165135500745","solution_id":null,"answer_id":null,"prompt_mn":["2","1","2"],"answer_mn":[],"list_id":null},{"number":7,"id":"fs-id1165137854912","problem_id":"fs-id1165134312130","prompt_id":"fs-id1165134312132","solution_id":"fs-id1165137731586","answer_id":"fs-id1165137731589","prompt_mn":["5","2","2"],"answer_mn":[],"list_id":null},{"number":8,"id":"fs-id1165135512534","problem_id":"fs-id1165135512537","prompt_id":"fs-id1165137804475","solution_id":null,"answer_id":null,"prompt_mn":["3","2"],"answer_mn":[],"list_id":null},{"number":9,"id":"fs-id1165137473385","problem_id":"fs-id1165137473388","prompt_id":"fs-id1165134374059","solution_id":"fs-id1165137451053","answer_id":"fs-id1165137451055","prompt_mn":["3","6","2"],"answer_mn":["3"],"list_id":null},{"number":10,"id":"fs-id1165135192268","problem_id":"fs-id1165135192270","prompt_id":"fs-id1165137725224","solution_id":null,"answer_id":null,"prompt_mn":["4","3"],"answer_mn":[],"list_id":null},{"number":11,"id":"fs-id1165137629066","problem_id":"fs-id1165137483196","prompt_id":"fs-id1165137483198","solution_id":"fs-id1165134192936","answer_id":"fs-id1165137463777","prompt_mn":["2","4"],"answer_mn":[],"list_id":null},{"number":12,"id":"fs-id1165137807107","problem_id":"fs-id1165137551129","prompt_id":"fs-id1165137551131","solution_id":null,"answer_id":null,"prompt_mn":["1","2","3"],"answer_mn":[],"list_id":null},{"number":13,"id":"fs-id1165134259277","problem_id":"fs-id1165134259279","prompt_id":"fs-id1165135186001","solution_id":"fs-id1165134058389","answer_id":"fs-id1165137836596","prompt_mn":["1","3"],"answer_mn":[],"list_id":null},{"number":14,"id":"fs-id1165135503751","problem_id":"fs-id1165134156030","prompt_id":"fs-id1165134156032","solution_id":null,"answer_id":null,"prompt_mn":["9","6"],"answer_mn":[],"list_id":null},{"number":15,"id":"fs-id1165133276237","problem_id":"fs-id1165133276240","prompt_id":"fs-id1165137784864","solution_id":"fs-id1165137454548","answer_id":"fs-id1165134170171","prompt_mn":["3","1","4","2"],"answer_mn":["1","2","1","2"],"list_id":null},{"number":16,"id":"fs-id1165137810520","problem_id":"fs-id1165137810522","prompt_id":"fs-id1165137532795","solution_id":null,"answer_id":null,"prompt_mn":["4","4"],"answer_mn":[],"list_id":null},{"number":17,"id":"fs-id1165135548992","problem_id":"fs-id1165135634123","prompt_id":"fs-id1165135634125","solution_id":"fs-id1165137528909","answer_id":"fs-id1165137528911","prompt_mn":["3","2","9","22"],"answer_mn":["11","11","2","2"],"list_id":null},{"number":18,"id":"fs-id1165135593402","problem_id":"fs-id1165135593404","prompt_id":"fs-id1165137771850","solution_id":null,"answer_id":null,"prompt_mn":["1","2","6"],"answer_mn":[],"list_id":null},{"number":19,"id":"fs-id1165135191342","problem_id":"fs-id1165134284474","prompt_id":"fs-id1165134284476","solution_id":"fs-id1165135256053","answer_id":"fs-id1165135256055","prompt_mn":["2","3","250","2","2","15"],"answer_mn":["3","3","5","5"],"list_id":null},{"number":20,"id":"fs-id1165137921795","problem_id":"fs-id1165137921797","prompt_id":"fs-id1165137532172","solution_id":null,"answer_id":null,"prompt_mn":["5","3"],"answer_mn":[],"list_id":null},{"number":21,"id":"fs-id1165137476914","problem_id":"fs-id1165137476916","prompt_id":"fs-id1165137726504","solution_id":"fs-id1165137647829","answer_id":"fs-id1165137564959","prompt_mn":["2","1","5"],"answer_mn":["5"],"list_id":null},{"number":22,"id":"fs-id1165135185292","problem_id":"fs-id1165137640755","prompt_id":"fs-id1165137640757","solution_id":null,"answer_id":null,"prompt_mn":["4","6"],"answer_mn":[],"list_id":null},{"number":23,"id":"fs-id1165135252252","problem_id":"fs-id1165137611840","prompt_id":"fs-id1165137611842","solution_id":"fs-id1165137611238","answer_id":"fs-id1165137538970","prompt_mn":["6","4"],"answer_mn":["6"],"list_id":null},{"number":24,"id":"fs-id1165137601712","problem_id":"fs-id1165137601714","prompt_id":"fs-id1165137657487","solution_id":null,"answer_id":null,"prompt_mn":[],"answer_mn":[],"list_id":null},{"number":25,"id":"fs-id1165137628472","problem_id":"fs-id1165137651574","prompt_id":"fs-id1165137651576","solution_id":"fs-id1165135188135","answer_id":"fs-id1165137809882","prompt_mn":["2","9","2","81"],"answer_mn":["9","9","9","9"],"list_id":null},{"number":26,"id":"fs-id1165137469452","problem_id":"fs-id1165137469454","prompt_id":"fs-id1165137635293","solution_id":null,"answer_id":null,"prompt_mn":["2","3","50"],"answer_mn":[],"list_id":"fs-id1165137938832"}]''')

# Intervals are (lower, upper, includes_lower, includes_upper); None is infinity.
ALL = ((None, None, False, False),)
DOMAINS = {
    6: ALL, 7: ALL, 8: ((F(2), None, True, False),),
    9: ((None, F(3), False, True),),
    10: ((None, F(4, 3), False, True),), 11: ALL, 12: ALL, 13: ALL,
    14: ((None, F(6), False, False), (F(6), None, False, False)),
    15: ((None, F(-1, 2), False, False), (F(-1, 2), None, False, False)),
    16: ((F(-4), F(4), True, False), (F(4), None, False, False)),
    17: ((None, F(-11), False, False), (F(-11), F(2), False, False), (F(2), None, False, False)),
    18: ((None, F(-2), False, False), (F(-2), F(3), False, False), (F(3), None, False, False)),
    19: ((None, F(-3), False, False), (F(-3), F(5), False, False), (F(5), None, False, False)),
    20: ((F(3), None, False, False),), 21: ((None, F(5), False, False),),
    22: ((F(6), None, False, False),), 23: ((F(6), None, True, False),),
    24: ((None, F(0), False, False), (F(0), None, False, False)),
    25: ((None, F(-9), False, False), (F(-9), F(9), False, False), (F(9), None, False, False)),
    26: ((F(-5), F(0), True, True), (F(5), None, True, False)),
}
NEW_INTERVALS = {
    6: r"(-\infty,\infty)", 8: r"[2,\infty)", 10: r"(-\infty,\frac43]",
    12: r"(-\infty,\infty)", 14: r"(-\infty,6)\cup(6,\infty)",
    16: r"[-4,4)\cup(4,\infty)", 18: r"(-\infty,-2)\cup(-2,3)\cup(3,\infty)",
    20: r"(3,\infty)", 22: r"(6,\infty)", 24: r"(-\infty,0)\cup(0,\infty)",
    26: r"[-5,0]\cup[5,\infty)",
}


def defined(number, x):
    """Real-domain restrictions read independently from the original formulas."""
    if number in (6, 7, 12, 13):
        return True
    return {
        8: x - 2 >= 0,
        9: 6 - 2*x >= 0,
        10: 4 - 3*x >= 0,
        11: x*x + 4 >= 0,
        14: x - 6 != 0,
        15: 4*x + 2 != 0,
        16: x + 4 >= 0 and x - 4 != 0,
        17: x*x + 9*x - 22 != 0,
        18: x*x - x - 6 != 0,
        19: x*x - 2*x - 15 != 0,
        20: x - 3 > 0,
        21: 5 - x > 0,
        22: x - 4 >= 0 and x - 6 > 0,
        23: x - 6 >= 0 and x - 4 > 0,
        24: x != 0,
        25: x*x - 81 != 0,
        26: 2*x**3 - 50*x >= 0,
    }[number]


def in_intervals(x, intervals):
    return any((a is None or x > a or (lc and x == a))
               and (b is None or x < b or (rc and x == b))
               for a, b, lc, rc in intervals)


def math_text(node):
    """Read the simple source interval answers, retaining fractional endpoints."""
    if node.tag == M + "mfrac":
        return math_text(node[0]) + "/" + math_text(node[1])
    return (node.text or "").strip() + "".join(math_text(child) for child in node)


def parse_intervals(node):
    values = []
    for part in math_text(node).split("∪"):
        match = re.fullmatch(r"([\(\[])([^,]+),([^,\]\)]+)([\)\]])", part)
        assert match, part
        left, a, b, right = match.groups()
        convert = lambda value: None if "∞" in value else F(value.replace("−", "-"))
        values.append((convert(a), convert(b), left == "[", right == "]"))
    return tuple(values)


def poly_mul(a, b):
    values = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            values[i+j] += x*y
    return values


def math_signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((math_signature(child), (child.tail or "").strip()) for child in node))


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, message, kind="source_structure_asset"):
        assert condition, message
        counts[kind] += 1

    excerpt_path = ROOT / "sources/m49304-algebraic-domains-source.cnxml"
    draft_path = ROOT / "translation/A30-U025-algebraic-domains.vi.md"
    extractor_path = ROOT / "tools/extract_algebraic_domains.py"
    checker_path = Path(__file__).resolve()
    generator_path = ROOT / "computing/generate_U025_radicand_plot.py"
    canon_path = ROOT / "canon/review-A30-U025.json"
    provenance_path = ROOT / "provenance/U025-source-review.json"
    data = excerpt_path.read_bytes()
    canon_data = canon_path.read_bytes()
    canon = json.loads(canon_data)
    provenance = json.loads(provenance_path.read_bytes())
    source = ET.fromstring(data)
    md_data = draft_path.read_bytes()
    md = md_data.decode("utf-8")
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", md)
    expected_anchor_order = [SECTION, "fs-id1165137408926"]
    expected_anchor_order += [identity for item in ITEMS
                              for identity in (item["id"], item["problem_id"],
                                               item["prompt_id"], item["list_id"])
                              if identity]
    expected_anchor_order += [identity for item in ITEMS
                              for identity in (item["solution_id"], item["answer_id"])
                              if identity]
    check(sha256(data).hexdigest() == EXCERPT_SHA
          and provenance["source_excerpt_sha256"] == EXCERPT_SHA
          and canon["source_excerpt_sha256"] == EXCERPT_SHA
          and provenance["extractor_sha256"] == sha256(extractor_path.read_bytes()).hexdigest()
          and provenance["computing_check_sha256"] == sha256(checker_path.read_bytes()).hexdigest()
          and provenance["plot_generator_sha256"] == sha256(generator_path.read_bytes()).hexdigest()
          and provenance["canon_review_sha256"] == sha256(canon_data).hexdigest(),
          "exact excerpt, extractor, checker, generator and canon bindings")
    check(md == unicodedata.normalize("NFC", md)
          and sha256(md_data).hexdigest() == DRAFT_SHA
          and provenance["translation_sha256"] == DRAFT_SHA
          and canon["translation_sha256"] == DRAFT_SHA,
          "NFC Vietnamese and exact draft bindings")
    check(len(by_id) == 86, "all86 source IDs")
    check(len(anchors) == len(set(anchors))
          and [anchor for anchor in anchors if anchor in by_id] == expected_anchor_order,
          "no duplicate anchors and exact designed source-anchor order")
    for identity in by_id:
        check(anchors.count(identity) == 1, f"anchor once: m49304/{identity}")
    for tag, expected in (("section",1), ("exercise",21), ("problem",21), ("solution",10),
                          ("image",0), ("example",0), ("list",1), ("item",2)):
        check(len(list(source.iter(CN + tag))) == expected, f"source {tag} count")
    check([n.get("id") for n in source.iter(CN + "exercise")] == [i["id"] for i in ITEMS],
          "all21 source exercises in order")
    check(re.findall(r"^### Bài (\d+) ", md, re.M) == [str(n) for n in range(6,27)],
          "visible source numbering6through26")
    source_maths = list(source.iter(M + "math"))
    check(len(source_maths) == 31, "31 source MathML expressions")
    captures = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", md):
        check(identity in by_id, "source math owner exists")
        options = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(options), "source math index valid")
        captures.append(options[int(index)])
    refs = [(identity, int(index)) for identity, index in
            re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", md)]
    expected_refs = [(item["prompt_id"], 0) for item in ITEMS]
    expected_refs += [(item["answer_id"], 0) for item in ITEMS if item["answer_id"]]
    check(refs == expected_refs
          and Counter(map(id,captures)) == Counter(map(id,source_maths)),
          "all31 MathML expressions captured exactly once in designed reader order")
    check(not list(source.iter(M+"mtext")), "zero mtext translation entries")
    solution_numbers = re.findall(r"^### Lời giải Bài (\d+) ", md, re.M)
    solution_bodies = re.findall(
        r"^### Lời giải Bài \d+ .*?(?=^### Lời giải Bài |^## Tự kiểm tra)", md, re.M | re.S)
    expected_source = {7, 9, 11, 13, 15, 17, 19, 21, 23, 25}
    labels = [(int(number), body.count("**Đáp án nguồn:**"),
               body.count("**Lời giải bổ sung — nguồn không kèm đáp án:**"))
              for number, body in zip(solution_numbers, solution_bodies)]
    check(labels == [(number, int(number in expected_source), int(number not in expected_source))
                     for number in range(6, 27)],
          "source and supplemental labels belong to the correct exercises")
    check(sum(source_count for _, source_count, _ in labels) == 10
          and sum(new_count for _, _, new_count in labels) == 11,
          "ten supplied and eleven new answers labeled")
    for item in ITEMS:
        number = item["number"]
        check([n.text for n in by_id[item["prompt_id"]].iter(M+"mn")] == item["prompt_mn"],
              f"unchanged source prompt numerals:{number}")
        check(by_id[item["id"]].find(CN+"problem").get("id") == item["problem_id"],
              f"unchanged source problem ID:{number}")
        target = item["solution_id"] or f"vi-sol-{number}"
        check(f"[Lời giải Bài {number}](#{target})" in md, f"answer link:{number}")
        check(f"[Trở lại Bài {number}](#{item['id']})" in md, f"backlink:{number}")
        if item["solution_id"]:
            answer = by_id[item["answer_id"]]
            check([n.text for n in answer.iter(M+"mn")] == item["answer_mn"],
                  f"unchanged supplied answer numerals:{number}")
            check(parse_intervals(answer) == DOMAINS[number],
                  f"supplied interval answer independently interpreted:{number}", "exact_math")
        else:
            start = md.index(f"### Lời giải Bài {number} ")
            end = md.index(f"[Trở lại Bài {number}]", start)
            check(NEW_INTERVALS[number] in md[start:end], f"reviewed new interval:{number}")
        probes = {F(-12), F(-1), F(0), F(1), F(12)}
        for a,b,_,_ in DOMAINS[number]:
            for endpoint in (a,b):
                if endpoint is not None:
                    probes.update((endpoint-F(1,10), endpoint, endpoint+F(1,10)))
        for x in sorted(probes):
            check(defined(number,x) == in_intervals(x,DOMAINS[number]),
                  f"exact rational domain witness:{number},x={x}", "finite_domain")
    local = re.findall(r"\]\(#([^)]*)\)", md)
    check(len(local) == 42 and all(anchors.count(target)==1 for target in local),
          "all42 local jump/backlinks resolve")
    check(not re.findall(r"\]\(A30-",md), "no cross-reader links")
    check([n.text for n in by_id["fs-id1165137938832"].iter(CN+"span")] == ["ⓐ","ⓑ"],
          "both source part glyphs")
    plain = " ".join(md.split())
    for phrase in ("tập xác định thực lớn nhất", "không quy định tập đầu vào khác",
                   "ô chỉ số rỗng", "căn bậc hai", "không khôi phục những đầu vào",
                   "Có thể lấy căn bậc ba của mọi số thực", "do nhóm dịch tạo mới",
                   "không phải hình nguồn", "các biên của khung không phải là biên của tập xác định",
                   "không thay thế lập luận đó"):
        check(phrase in plain, f"material qualification:{phrase}")
    special = by_id["fs-id1165137483198"]
    mroot = next(special.iter(M+"mroot"))
    check(len(mroot)==2 and mroot[1].tag==M+"mrow" and len(mroot[1])==0
          and not (mroot[1].text or "").strip(), "Bài11 exact empty-index root retained")
    table = next(special.iter(M+"mtable"))
    check(len(table)==2 and not "".join(table[0].itertext()).strip(),
          "Bài11 initial empty MathML table row retained")
    # Exact coefficient equalities verify factorization, not by numerical sampling.
    for factors, expected in (
        (([11,1],[-2,1]),[-22,9,1]),
        (([-3,1],[2,1]),[-6,-1,1]),
        (([-5,1],[3,1]),[-15,-2,1]),
        (([2],[-5,1],[25,5,1]),[-250,0,0,2]),
        (([-9,1],[9,1]),[-81,0,1]),
        (([0,1],[-9,1]),[0,-9,1]),
        (([2],[0,1],[-5,1],[5,1]),[0,-50,0,2]),
    ):
        actual = [1]
        for factor in factors:
            actual = poly_mul(actual,factor)
        check(actual==expected, f"exact coefficient factorization:{factors}", "exact_math")
    for number, excluded in ((19,F(5)),(24,F(0)),(25,F(9)),(25,F(-9))):
        check(not defined(number,excluded), f"cancellation does not restore {number}:{excluded}",
              "exact_math")
    check(defined(22,F(7)) and not defined(22,F(6)) and defined(23,F(6)),
          "swapped square-root denominators differ at6", "exact_math")
    check(defined(16,F(-4)) and not defined(16,F(4)),
          "sqrt numerator permitszero but denominator rejectszero", "exact_math")
    check(all(2*x**3-50*x==0 for x in (-5,0,5)), "three exact radicand zeros", "exact_math")
    check([2*x**3-50*x > 0 for x in (-6,-1,1,6)] == [False,True,False,True],
          "one exact sign witness in each factor interval", "finite_domain")
    png = (ROOT/"assets/A30-U025-radicand-sign.png").read_bytes()
    check(sha256(png).hexdigest()==PNG_SHA
          and provenance["new_plot"]["sha256"] == PNG_SHA
          and provenance["new_plot"]["bytes"] == len(png),
          "exact personally reviewed supplemental plot")
    plot_meta = provenance["new_plot"]
    check(png[:8]==b"\x89PNG\r\n\x1a\n"
          and struct.unpack(">II",png[16:24])==(1280,1280)
          and plot_meta["pixels"] == [1280, 1280]
          and plot_meta["window"] == {"xmin": -6, "xmax": 6, "ymin": -140, "ymax": 140}
          and plot_meta["zeros"] == [-5, 0, 5]
          and plot_meta["sample_count"] == 1201
          and plot_meta["dependencies"]["pillow"] == "12.3.0"
          and plot_meta["dependencies"]["font_sha256"] ==
              "b3658eadae55e682b5f69eb64c439c1ecc8f196c0bb8d4756d145d13bc86476a",
          "new PNG format/dimensions and deterministic metadata")
    check(md.count("![")==1 and "../assets/A30-U025-radicand-sign.png" in md,
          "one new plot, zero source images")

    if originals:
        sys.path.insert(0,str(ROOT/"tools"))
        from extract_algebraic_domains import ORIGINALS, extract
        for language, (relative,digest) in zip(("en", "id"), ORIGINALS):
            path=ROOT.parent/relative
            check(sha256(path.read_bytes()).hexdigest()==digest
                  and provenance["source_module_sha256"][language] == digest,
                  "pinned original and provenance binding","originals")
            reproduced=extract(path)
            original=ET.fromstring(reproduced)
            check([n.get("id") for n in original.iter() if n.get("id")]==list(by_id),
                  "EN/ID ordered86 identities","originals")
            check([math_signature(n) for n in original.iter(M+"math")] ==
                  [math_signature(n) for n in source_maths],
                  "all31 EN/ID original MathML identical","originals")
            check([n.get("id") for n in original.iter(CN+"solution")] ==
                  [i["solution_id"] for i in ITEMS if i["solution_id"]],
                  "EN/ID ten identical source-answer slots","originals")
            if "upstream-openstax" in relative:
                check(reproduced.encode("utf-8")==data,"complete EN section reproduced","originals")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result=tests(originals="--originals" in sys.argv,details=True)
    print(f"PASS: {sum(result.values())} mixed assertions; {result}; finite probes are not proofs")
