"""U029 source/assets checks and finite reciprocal-range witnesses.

No reader is built and no file is written. Range proofs are in the Vietnamese
draft; finite samples (including plotted batches) are not universal proofs.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose
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
EXCERPT_SHA = "da246d7948856e53fea3456fa045d60d21aaedabd1d4191b360c5e0a9317e19c"
IDS = [
  "fs-id1165135194497",
  "fs-id1165137780865",
  "fs-id1165137780867",
  "fs-id1165135641711",
  "fs-id1165137501974",
  "fs-id1165134258632",
  "fs-id1165135191028",
  "fs-id1165137442910",
  "fs-id1165134378637",
  "fs-id1165131911953",
  "fs-id1165137842479",
  "fs-id1165137842481"
]
KEYS = [
  [
    "fs-id1165135641711",
    0
  ],
  [
    "fs-id1165135641711",
    1
  ],
  [
    "fs-id1165135641711",
    2
  ],
  [
    "fs-id1165135191028",
    0
  ],
  [
    "fs-id1165135191028",
    1
  ],
  [
    "fs-id1165134378637",
    0
  ],
  [
    "fs-id1165134378637",
    1
  ],
  [
    "fs-id1165137842481",
    0
  ],
  [
    "fs-id1165137842481",
    1
  ],
  [
    "fs-id1165137842481",
    2
  ]
]
NUMERIC = {
  "fs-id1165135641711": [
    "1",
    "2",
    "−0.5",
    "−0.1",
    "0.1",
    "0.5"
  ],
  "fs-id1165135191028": [
    "0.5",
    "0.1",
    "4",
    "100"
  ],
  "fs-id1165134378637": [
    "0.1",
    "0.5",
    "4",
    "100"
  ],
  "fs-id1165137842481": [
    "1",
    "−0.5",
    "−0.1",
    "0.1",
    "0.5"
  ]
}
ASSETS = [
  {
    "rights_component_id": "rights:openstax-precalculus-2e:asset:006e2030084deb57b493dadc",
    "asset_path": "media/CNX_Precalc_Figure_01_02_221.jpg",
    "bytes": "90410",
    "sha256": "ed1428ec19872bf45a2b362214f83e260d2b84bd1282607444567ed95e76e25d",
    "source_modules": "m49304",
    "classification": "WORK_DEFAULT_UNCREDITED_ART",
    "admission": "admitted",
    "license_id": "CC-BY-NC-SA-4.0",
    "attribution": "Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0.",
    "required_action": "Preserve work attribution, change notice, ShareAlike, and non-endorsement."
  },
  {
    "rights_component_id": "rights:openstax-precalculus-2e:asset:d86063bccd0164b7f551b2e0",
    "asset_path": "media/CNX_Precalc_Figure_01_02_222-1958.jpg",
    "bytes": "92256",
    "sha256": "a9332873db443152a1d520ede0ee053114a2e5c0df5813920e4bb2356bd83fa2",
    "source_modules": "m49304",
    "classification": "WORK_DEFAULT_UNCREDITED_ART",
    "admission": "admitted",
    "license_id": "CC-BY-NC-SA-4.0",
    "attribution": "Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0.",
    "required_action": "Preserve work attribution, change notice, ShareAlike, and non-endorsement."
  }
]
NEW_HASHES = {
  "negative": "1b6f53d9081ddbe31b503771837365b66cace25abbdde6df7db7dad096373e3d",
  "positive": "4bcb44522dcbee29df761c4b1cd39afe3d8ef3484b2e988bc6820d7696b8b783"
}


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(c), (c.tail or "").strip()) for c in node))


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

    data = (ROOT/"sources/m49304-reciprocal-windows-source.cnxml").read_bytes()
    source = ET.fromstring(data)
    draft = (ROOT/"translation/A30-U029-reciprocal-windows.vi.md").read_text(encoding="utf-8")
    by_id = {n.get("id"):n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(sha256(data).hexdigest() == EXCERPT_SHA, "exact source excerpt")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    check(list(by_id) == IDS, "12sourceIDs in exact order")
    check(all(v == 1 for v in Counter(anchors).values()), "unique anchors")
    for identity in IDS:
        check(anchors.count(identity) == 1, "source anchor "+identity)
    check([n.get("id") for n in source.iter(CN+"section")] == ["fs-id1165135194497"],
          "Technology only; no outer heading or Extensions content")
    check([n.get("id") for n in source.iter(CN+"exercise")] ==
          ["fs-id1165137780865","fs-id1165131911953"], "two exercises in source order")
    check([n.get("id") for n in source.iter(CN+"solution")] == ["fs-id1165137501974"],
          "only exercise55 has an original answer")
    check(by_id["fs-id1165131911953"].find(CN+"solution") is None, "exercise56 new answer needed")
    check(re.findall(r"### Bài (\d+)",draft) == ["55","56"], "global exercise numbering")
    check(draft.count("**Đáp án nguồn.**") == 1, "one source answer label")
    check(draft.count("**Lời giải bổ sung — nguồn không kèm đáp án.**") == 1, "one new answer label")
    check(draft.count("**Hình bổ sung — tạo mới cho Bài 56, không phải hình nguồn.**") == 2,
          "both new figures explicitly labeled")
    refs = [[i,int(j)] for i,j in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}",draft)]
    check(refs == KEYS, "ten original MathML references in order")
    maths = list(source.iter(M+"math"))
    used = [list(by_id[i].iter(M+"math"))[j] for i,j in refs]
    check(len(maths) == 10 and Counter(map(id,used)) == Counter(map(id,maths)), "all10MathML once")
    check(not list(source.iter(M+"mtext")), "no MathML prose localization")
    check(not list(source.iter(M+"mroot")) and not list(source.iter(M+"msqrt")), "no source roots")
    for owner,expected in NUMERIC.items():
        check([n.text for n in by_id[owner].iter(M+"mn")] == expected, "numeric tokens "+owner)
    check(not list(source.iter(CN+"link")) and not re.findall(r"\]\(#|\]\(A30-",draft),
          "no crossreference dependency")
    images = re.findall(r"!\[(.*?)\]\(([^)]+)\)",draft)
    expected_images = ["../assets/"+Path(a["asset_path"]).name for a in ASSETS]
    expected_images += ["../assets/A30-U029-ex56-negative.png","../assets/A30-U029-ex56-positive.png"]
    check([p for _,p in images] == expected_images, "two original and two new figures in order")
    check(all(len(alt) > 100 for alt,_ in images), "complete Vietnamese alt descriptions")
    check([n.get("src") for n in source.iter(CN+"image")] ==
          ["../../"+a["asset_path"] for a in ASSETS], "all original media references")
    flat = " ".join(draft.split())
    for phrase in ("không phải một tập giá trị", "Cả hai đầu mút", "không nối hai phần đồ thị",
                   "Khung ảnh có thêm vùng ngoài đoạn", "Không đọc biên khung",
                   "dù ảnh không đánh dấu", "không có khoảng trống ở giữa",
                   "với mỗi $y", "không phải theo thứ tự gặp", "không chỉ là kiểm tra các đầu mút",
                   "không phải tập giá trị $[2,10]$", "không thay thế"):
        check(phrase in flat, "important qualification "+phrase)

    generator = load_helper("u029_plot",ROOT/"computing/generate_U029_reciprocal_plots.py")
    math_start = count
    magnitudes = [F(1,10),F(1,5),F(1,4),F(2,5),F(1,2)]
    reciprocals = [10,5,4,F(5,2),2]
    squares = [100,25,16,F(25,4),4]
    for sign in (-1,1):
        for t,reciprocal,squared in zip(magnitudes,reciprocals,squares):
            x=sign*t
            check(1/(x*x) == squared, "reciprocal-square rational value")
            check(1/x == sign*reciprocal, "reciprocal rational value")
            check(4 <= 1/(x*x) <= 100, "reciprocal-square window sample bound")
            lo,hi=(-10,-2) if sign<0 else (2,10)
            check(lo <= 1/x <= hi, "reciprocal window sample bound")
        for yroot in range(2,11):
            x=F(sign,yroot)
            lo,hi=(F(-1,2),F(-1,10)) if sign<0 else (F(1,10),F(1,2))
            check(lo <= x <= hi and 1/(x*x) == yroot*yroot, "square-range preimage witness")
        for magnitude in range(2,11):
            y=sign*magnitude; x=F(1,y)
            check(lo <= x <= hi and 1/x == y, "reciprocal-range preimage witness")
    for x,allowed in ((-100,True),(-1,True),(F(-1,2),True),(0,False),
                      (F(1,2),True),(1,True),(100,True)):
        check((x != 0) == allowed, "natural denominator domain witness")
    for root in (F(1,10),F(1,2),F(1),F(2),F(10)):
        x=1/root
        check(1/(x*x) == root*root and root*root>0, "global positive-square-range witness")
    for y in (F(-100),F(-1,3),F(1,100),F(1),F(100)):
        x=1/y
        check(x != 0 and 1/x == y, "global reciprocal nonzero-range witness")
    for key,expected in (("negative",((-0.5,-2),(-0.1,-10))),
                         ("positive",((0.1,10),(0.5,2)))):
        points=generator.curve_points(key); spec=generator.SPECS[key]
        lo,hi=spec["domain"]; low,high=spec["range"]
        check(all(isclose(y,1/x,rel_tol=1e-12) for x,y in points), "all601 plotted values")
        check(all(lo-1e-12 <= x <= hi+1e-12 for x,y in points), "all601 plotted inputs restricted")
        check(all(low-1e-12 <= y <= high+1e-12 for x,y in points), "all601 plotted outputs bounded")
        check(all(points[i][0] < points[i+1][0] and points[i][1] > points[i+1][1]
                  for i in range(len(points)-1)), "600strict-decrease plot steps")
        for actual,endpoint in zip((points[0],points[-1]),expected):
            check(all(isclose(a,b,abs_tol=1e-12) for a,b in zip(actual,endpoint)), "included plot endpoint")
    math_count=count-math_start

    ledger=ROOT.parent/"downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rows={}
    if ledger.is_file():
        rows={r["asset_path"]:r for r in csv.DictReader(ledger.open(encoding="utf-8-sig",newline=""))}
    for asset in ASSETS:
        name=Path(asset["asset_path"]).name
        candidates=[ROOT/"assets"/name,ROOT.parent/"downloads/upstream-openstax/media"/name]
        present=[p for p in candidates if p.is_file()]
        check(bool(present), "original asset available "+name)
        check(all(sha256(p.read_bytes()).hexdigest() == asset["sha256"] for p in present),
              "all available original copies have inherited admitted hash "+name)
        check(all(p.stat().st_size == int(asset["bytes"]) for p in present), "original byte size "+name)
        if rows:
            check(rows.get(asset["asset_path"]) == asset, "exact inherited rights row "+name)
    for key,digest in NEW_HASHES.items():
        p=ROOT/f"assets/A30-U029-ex56-{key}.png"
        check(p.is_file() and sha256(p.read_bytes()).hexdigest() == digest, "new image bound "+key)
        check(len(generator.curve_points(key)) == 601, "deterministic sampling count "+key)
    extractor=load_helper("u029_extract",ROOT/"tools/extract_reciprocal_windows.py")
    for label,path in (
        ("en",ROOT.parent/"downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id",ROOT.parent/"downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if path.is_file():
            selected=ET.fromstring(extractor.extract(path))
            check([n.get("id") for n in selected.iter() if n.get("id")] == IDS, "original IDs "+label)
            check([canonical(n) for n in selected.iter(M+"math")] == [canonical(n) for n in maths],
                  "complete original mathematical structure "+label)
            check(len(list(selected.iter(CN+"solution"))) == 1, "original answer presence "+label)
            if label == "en":
                check(extractor.extract(path) == data.decode("utf-8"), "byte-reproducible source excerpt")
                check(canonical(selected) == canonical(source), "complete English content retained")
    return {"total":count,"source_structure_assets":count-math_count,"finite_mathematical":math_count}


if __name__=="__main__":
    result=tests()
    print(f"PASS: {result['total']} mixed assertions "
          f"({result['source_structure_assets']} source/structure/assets; "
          f"{result['finite_mathematical']} finite mathematical assertions, including plot batches)")
