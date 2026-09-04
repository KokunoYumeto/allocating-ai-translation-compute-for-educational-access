"""U027 source/structure/assets and finite piecewise graph checks.

Original answers and new plots are distinguished. Finite samples do not prove
entire domains, and this checker does not replace visual inspection or build.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import sqrt
from pathlib import Path
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
EXCERPT_SHA = "e3e8f747b3ad556c613df69099d45e526e889dc8aba9e6f376bfe24e604664c3"
ASSETS = [
  {
    "media_id": "fs-id1165137662700",
    "filename": "CNX_Precalc_Figure_01_02_214.jpg",
    "sha256": "91571413c00b8a4fed74fed9b9b641df93743affede04db4a56b62af2d7d5573",
    "bytes": 53991,
    "rights_component_id": "rights:openstax-precalculus-2e:asset:ca829a8728403e9399769141"
  },
  {
    "media_id": "fs-id1165137474386",
    "filename": "CNX_Precalc_Figure_01_02_216.jpg",
    "sha256": "cdd47a96bb917ded925abebd7131b80912d48337190db86b73f7a9483a0c0a4c",
    "bytes": 47155,
    "rights_component_id": "rights:openstax-precalculus-2e:asset:5ba9b43a2cac88322a138089"
  },
  {
    "media_id": "fs-id1165135188662",
    "filename": "CNX_Precalc_Figure_01_02_218.jpg",
    "sha256": "ed8d42e8e6fae7017652fda9fb1d376b181f0100a6f03a6b62d6d3c2e772b515",
    "bytes": 52064,
    "rights_component_id": "rights:openstax-precalculus-2e:asset:dafdf8dca922a5150ffd3479"
  },
  {
    "media_id": "fs-id1165135432997",
    "filename": "CNX_Precalc_Figure_01_02_220.jpg",
    "sha256": "c04a023cbce0ead324957ae34d7743181979c0b943d43311607e97723e73fa8e",
    "bytes": 56121,
    "rights_component_id": "rights:openstax-precalculus-2e:asset:746e534f56e59cfae8ab8fab"
  }
]
GENERATED = [
  {
    "exercise": 38,
    "filename": "A30-U027-ex38.png",
    "sha256": "48a5ba92e9a13f67ee9a66fac985f37bb7dd969ee4a9e9f79fade65189802529",
    "bytes": 54806,
    "window": [
      -6,
      3,
      -10,
      4
    ]
  },
  {
    "exercise": 40,
    "filename": "A30-U027-ex40.png",
    "sha256": "58bb54ee41a1306e8b8ebcb54d044121960d9e30b2039d4f5eb0f4698ed22c87",
    "bytes": 50953,
    "window": [
      -4,
      4,
      -4,
      4
    ]
  },
  {
    "exercise": 42,
    "filename": "A30-U027-ex42.png",
    "sha256": "d42b62958d278ca88ff55300c65c82673c49f369d768e4218afeb928346134ab",
    "bytes": 53640,
    "window": [
      -3,
      4,
      -4,
      10
    ]
  },
  {
    "exercise": 44,
    "filename": "A30-U027-ex44.png",
    "sha256": "8ea9df7825580dcf1317dee6ba9b47a7faf9223c88d16efd3aa6b6d8cb4d49e1",
    "bytes": 48169,
    "window": [
      -4,
      2,
      -4,
      10
    ]
  }
]
NUMERIC = {
  "fs-id1165137408527": [
    "1",
    "2",
    "2",
    "3",
    "2"
  ],
  "fs-id1165134328322": [
    "2",
    "1",
    "1",
    "1",
    "1"
  ],
  "fs-id1165137658062": [
    "1",
    "0",
    "1",
    "0"
  ],
  "fs-id1165133402089": [
    "3",
    "0",
    "0"
  ],
  "fs-id1165137400953": [
    "2",
    "0",
    "1",
    "0"
  ],
  "fs-id1165135210031": [
    "2",
    "2",
    "0",
    "0"
  ],
  "fs-id1165137433002": [
    "1",
    "1",
    "3",
    "1"
  ],
  "fs-id1165137554127": [
    "1",
    "2",
    "2"
  ]
}
EXERCISES = ["fs-id1165137462167", "fs-id1165137562309", "fs-id1165137628033",
             "fs-id1165135641679", "fs-id1165135192719", "fs-id1165137594981",
             "fs-id1165137571389", "fs-id1165137407891"]
SOLUTIONS = ["fs-id1165135481131", "fs-id1165137500956", "fs-id1165137667233", "fs-id1165137401041"]
VALUES = {
    38: [-3,-2,1,-1,-3,-5,-7,-9,-11],
    39: [-9,-7,-5,-3,-1,2,3,4,5],
    40: [-3,-2,-1,0,None,0,1,2,3],
    41: [3,3,3,3,0,1,2,3,4],
    42: [16,9,4,1,None,0,-1,-2,-3],
    43: [16,9,4,1,2,3,4,5,6],
    44: [-3,-2,-1,0,1,1,8,27,64],
    45: [4,3,2,1,0,1,1,1,1],
}
ENDPOINTS = {
    38: [(-2,-1,False),(-2,1,True)],
    39: [(1,1,False),(1,2,True)],
    40: [(0,1,False),(0,-1,False)],
    41: [(0,3,False),(0,0,True)],
    42: [(0,0,False),(0,1,False)],
    43: [(0,0,False),(0,2,True)],
    44: [(1,2,False),(1,1,True)],
    45: [(2,2,False),(2,1,True)],
}


def value(number, x):
    if number == 38:
        return x+1 if x < -2 else -2*x-3
    if number == 39:
        return 2*x-1 if x < 1 else x+1
    if number == 40:
        return None if x == 0 else (x+1 if x < 0 else x-1)
    if number == 41:
        return 3 if x < 0 else sqrt(x)
    if number == 42:
        return None if x == 0 else (x*x if x < 0 else 1-x)
    if number == 43:
        return x*x if x < 0 else x+2
    if number == 44:
        return x+1 if x < 1 else x*x*x
    if number == 45:
        return abs(x) if x < 2 else 1
    raise ValueError(number)


def canonical(node, language="en"):
    text = (node.text or "").strip()
    if language == "id" and node.tag == M+"mtext":
        text = text.replace("jika", "if")
    return (node.tag, tuple(sorted(node.attrib.items())), text,
            tuple((canonical(child, language), (child.tail or "").strip()) for child in node))


def load_helper(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tests():
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    data = (ROOT/"sources/m49304-piecewise-graph-exercises-source.cnxml").read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned exact selected source fragment")
    source = ET.fromstring(data)
    draft = (ROOT/"translation/A30-U027-piecewise-graph-exercises.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    by_id = {n.get("id"):n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(by_id) == 37, "37 module-local source IDs")
    check(all(n == 1 for n in Counter(anchors).values()), "unique draft anchors")
    for identity in by_id:
        check(anchors.count(identity) == 1, "retained source ID "+identity)
    check("fs-id1165137580833" not in by_id and "fs-id1165134118450" not in by_id,
          "no duplicate Graphical parent or following Numeric content")
    selected = list(source.find(CN+"content/"+CN+"section"))
    check(selected[0].get("id") == "fs-id1165137785119" and
          [n.get("id") for n in selected[1:]] == EXERCISES, "shared instruction and8exercises in order")
    check([n.get("id") for n in source.iter(CN+"solution")] == SOLUTIONS, "four source answers")
    check([38+i for i,e in enumerate(EXERCISES) if by_id[e].find(CN+"solution") is None] ==
          [38,40,42,44], "exact missing-answer exercises")
    check(draft.count("**Đáp án nguồn.**") == 4, "four source labels")
    check(draft.count("**Lời giải bổ sung — nguồn không kèm đáp án.**") == 4, "four new answer labels")
    check(re.findall(r"### Bài (\d+)", draft) == list(map(str,range(38,46))), "continuous numbering38–45")
    maths = list(source.iter(M+"math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    nodes = [list(by_id[i].iter(M+"math"))[int(j)] for i,j in refs]
    check(len(refs) == len(maths) == 12, "twelve source math occurrences")
    check(Counter(map(id,nodes)) == Counter(map(id,maths)), "allsourceMathML once")
    for identity, expected in NUMERIC.items():
        check([n.text for n in by_id[identity].iter(M+"mn")] == expected, "numeric tokens "+identity)
    mtext = [n.text for n in source.iter(M+"mtext")]
    check(len(mtext) == 16 and all(t.strip() == "if" for t in mtext), "16ifmtext nodes with source padding")
    check(all(t.replace("if","nếu").replace("nếu","if") == t for t in mtext),
          "prose-only mtext localization reversible with padding intact")
    check(not list(source.iter(M+"mroot")) and len(list(source.iter(M+"msqrt"))) == 1,
          "one ordinary square root; no empty-index root in this slice")
    check(len(list(source.iter(CN+"image"))) == 4 and not list(source.iter(CN+"figure")),
          "four bare source solution images")
    check(not list(source.iter(CN+"link")) and not re.findall(r"\]\(#",draft),
          "no source or local crossreference dependency")
    flat = " ".join(draft.split())
    for phrase in ("Tập xác định của hàm số là **hợp**", "không phải giao", "đồng thời",
                   "tập xác định là $(-\\infty,0)\\cup(0,\\infty)$", "nhánh hằng nhận",
                   "đường cong bậc ba", "đỉnh $(0,0)$ thuộc đồ thị", "không phải hình nguồn",
                   "không thay thế lập luận"):
        check(phrase in flat, "important branch/source qualification "+phrase)
    for n in (38,40,42,44):
        check(f"tạo mới cho Bài {n}" in draft, "new image attributed as supplemental")
    images = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    expected_images = []
    for n in range(38,46):
        filename = f"A30-U027-ex{n}.png" if n in (38,40,42,44) else ASSETS[(n-39)//2]["filename"]
        expected_images.append("../assets/"+filename)
    check([path for _,path in images] == expected_images, "four new and four original image order")
    check(all(len(alt)>100 for alt,_ in images), "substantial Vietnamese alt for all8images")

    generator = load_helper("u027_plot", ROOT/"computing/generate_U027_piecewise_plots.py")
    math_start = count
    for number, expected in VALUES.items():
        xs = [-4,-3,-2,-1,0,1,4,9,16] if number == 41 else list(range(-4,5))
        for x,y in zip(xs,expected):
            check(value(number,x) == y, f"exercise{number} value at{x}")
        for x,y,included in ENDPOINTS[number]:
            check((value(number,x) == y) == included, f"exercise{number} open/closed point{x,y}")
        probes = [-100,-4,F(-5,2),-2,F(-1,2),0,F(1,2),1,2,4,100]
        check(all((value(number,x) is not None) == (number not in (40,42) or x != 0) for x in probes),
              f"exercise{number} finite domain-union probes")
    #One batch assertion for each generated graph compares800interior samples.
    for number in (38,40,42,44):
        points = generator.branch_points(number,"left")[:-1] + generator.branch_points(number,"right")[1:]
        check(all(value(number,x) == y for x,y in points), f"generated plot{number} interior formulas")
    assert count-math_start == 100

    ledger_path = ROOT.parent/"downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rows = {}
    if ledger_path.is_file():
        with ledger_path.open(encoding="utf-8-sig",newline="") as handle:
            rows = {row["asset_path"]:row for row in csv.DictReader(handle)}
    for asset in ASSETS:
        check(by_id[asset["media_id"]].find(CN+"image").get("src") == "../../media/"+asset["filename"],
              "exact original source image reference")
        copies = [p for p in (ROOT/"assets"/asset["filename"],
                             ROOT.parent/"downloads/upstream-openstax/media"/asset["filename"]) if p.is_file()]
        check(bool(copies) and all(p.stat().st_size == asset["bytes"] and
                                  sha256(p.read_bytes()).hexdigest() == asset["sha256"] for p in copies),
              "unchanged original image bytes")
        if rows:
            row = rows["media/"+asset["filename"]]
            check(row["rights_component_id"] == asset["rights_component_id"] and
                  row["sha256"] == asset["sha256"] and row["admission"] == "admitted",
                  "inherited admitted asset row")
    for asset in GENERATED:
        path = ROOT/"assets"/asset["filename"]
        check(path.stat().st_size == asset["bytes"] and sha256(path.read_bytes()).hexdigest() == asset["sha256"],
              "pinned new plot bytes")
        spec = generator.SPECS[asset["exercise"]]
        check(list(spec["window"]) == asset["window"], "new plot window recorded")
        endpoint = ENDPOINTS[asset["exercise"]]
        check(spec["boundary"] == endpoint[0][0] and spec["left_closed"] == endpoint[0][2] and
              spec["right_closed"] == endpoint[1][2], "new plot endpoint marker semantics")
    extractor = load_helper("u027_extract", ROOT/"tools/extract_piecewise_graph_exercises.py")
    for language,path in (
        ("en",ROOT.parent/"downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id",ROOT.parent/"downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if not path.is_file():
            continue
        original = ET.fromstring(extractor.extract(path))
        check([n.get("id") for n in original.iter() if n.get("id")] == list(by_id), "original IDs "+language)
        check([canonical(n,language) for n in original.iter(M+"math")] ==
              [canonical(n) for n in maths], "exact original math exceptif/jika "+language)
        check([n.get("src") for n in original.iter(CN+"image")] ==
              [n.get("src") for n in source.iter(CN+"image")], "original image references "+language)
        check([n.get("id") for n in original.iter(CN+"solution")] == SOLUTIONS, "original answer presence "+language)
        if language == "en":
            check(extractor.extract(path) == data.decode("utf-8"), "reproducible exact English slice")
            check(canonical(original) == canonical(source), "allEnglish slice content retained")
    return count


if __name__=="__main__":
    print(f"PASS: {tests()} mixed source/structure/asset and finite mathematical assertions (100 finite mathematical assertions)")
