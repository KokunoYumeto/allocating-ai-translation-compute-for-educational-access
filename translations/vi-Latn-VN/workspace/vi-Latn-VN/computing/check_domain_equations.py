"""U018 source preservation, interval transcriptions and domain checks.

Finite samples and exact endpoint arithmetic are separate from analytic reasons
in the draft. Retain English original JPEGs; Indonesian localized SVG filenames
differ intentionally and are checked as an edition difference, not equality.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose, sqrt
from pathlib import Path
import csv
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"
EXCERPT_SHA = "fc3d65cca25e9b8e093a62f4c39995b55d9a312b10c16bae7fdc7e4a35d6c248"
ASSETS = [
    {
        "media_id": "fs-id1165135435537",
        "filename": "CNX_Precalc_Figure_01_02_001-f298.jpg",
        "sha256": "99d659c3caf07aac2e674f6354c699b28892b1a20ef98fca530a2ccf7a85c748",
        "bytes": 214119,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:729c80212e970d27f540550b",
        "id_image_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_001-id.svg"
    },
    {
        "media_id": "fs-id1165137737552",
        "filename": "CNX_Precalc_Figure_01_02_002-9aef.jpg",
        "sha256": "0dc77fa7e077f251c1ef204cf3d7e97f6d50bac1e0aced6ba2e7bd70c2c1ab6b",
        "bytes": 71257,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:71ffb1ec68de2dac5f095c58",
        "id_image_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_002-id.svg"
    },
    {
        "media_id": "fs-id1165137406680",
        "filename": "CNX_Precalc_Figure_01_02_029n.jpg",
        "sha256": "0970d52f02c750b0c5e62ae690349142c7337988324ee8dd6509860017795f0e",
        "bytes": 264222,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:2dd28164beb71361991c429a",
        "id_image_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_029n-id.svg"
    },
    {
        "media_id": "fs-id1165137434263",
        "filename": "CNX_Precalc_Figure_01_02_028n.jpg",
        "sha256": "f60d29fa3dc35f5d076fccfa5c8a84102d65cf393b164a54c5735ffc91dba559",
        "bytes": 45349,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:44cdceb54848b8ebf63c027e",
        "id_image_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_028n-id.svg"
    }
]
NUMBER_TOKENS = {
    "fs-id1165137761714": [
        "0",
        "100"
    ],
    "fs-id1165137920768": [
        "2",
        "10",
        "3",
        "10",
        "4",
        "20",
        "5",
        "30",
        "6",
        "40"
    ],
    "fs-id1165137451888": [
        "2",
        "3",
        "4",
        "5",
        "6"
    ],
    "fs-id1165137466017": [
        "−5",
        "4",
        "0",
        "0",
        "5",
        "−4",
        "10",
        "−8",
        "15",
        "−12"
    ],
    "fs-id1165137704712": [
        "5",
        "0",
        "5",
        "10",
        "15"
    ],
    "fs-id1165137645656": [
        "2",
        "1."
    ],
    "fs-id1165137871972": [
        "5",
        "3"
    ],
    "fs-id1165137647592": [
        "1",
        "2"
    ],
    "fs-id1165137736620": [
        "2",
        "0",
        "2",
        "2"
    ],
    "fs-id1165135192763": [
        "2",
        "2.",
        "2",
        "2"
    ],
    "fs-id1165134036054": [
        "2",
        "2"
    ],
    "fs-id1165137442339": [
        "1",
        "4",
        "2",
        "1"
    ],
    "fs-id1165135186314": [
        "1",
        "2",
        "1",
        "2"
    ],
    "fs-id1165137466144": [
        "7"
    ],
    "fs-id1165137727831": [
        "7",
        "0",
        "7",
        "7"
    ],
    "fs-id1165137422794": [
        "7",
        "7"
    ],
    "fs-id1165137452448": [
        "5",
        "2"
    ],
    "fs-id1165137832332": [
        "5",
        "2"
    ],
    "fs-id1165137937737": [
        "1"
    ]
}


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def tests():
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    path = ROOT / "sources/m49304-domain-equations-source.cnxml"
    data = path.read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned excerpt bytes")
    excerpt = ET.fromstring(data)
    source_text = data.decode("utf-8")
    draft = (ROOT / "translation/A30-U018-domain-equations.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    ids = [n.get("id") for n in excerpt.iter() if n.get("id")]
    by_id = {n.get("id"): n for n in excerpt.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(ids) == len(set(ids)) == 97, "97 distinct module-local source IDs")
    check(all(n == 1 for n in Counter(anchors).values()), "unique draft anchors")
    for identity in ids:
        check(anchors.count(identity) == 1, f"source anchor {identity}")
    math = list(excerpt.iter(M + "math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(refs) == len(math) == 32, "32 source MathML occurrences")
    captured = [list(by_id[identity].iter(M + "math"))[int(index)] for identity, index in refs]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "each source math occurrence exactly once")
    check(not list(excerpt.iter(M + "mtext")), "no source mtext replacements needed")
    for identity, expected in NUMBER_TOKENS.items():
        check([n.text for n in by_id[identity].iter(M + "mn")] == expected, f"source numeric tokens {identity}")
    check([n.get("id") for n in excerpt.iter(CN + "example")] ==
          [f"Example_01_02_0{i}" for i in range(1, 5)], "four complete examples in order")
    notes = list(excerpt.iter(CN + "note"))
    tries = [n for n in notes if "try" in n.get("class", "").split()]
    check(len(tries) == 4 and all(len(list(n.iter(CN + "solution"))) == 1 for n in tries),
          "four Try Its, each with source answer")
    check(len(list(excerpt.iter(CN + "solution"))) == 8, "eight source solutions/answers retained")
    check(draft.count("**Lời giải nguồn.**") == 4 and draft.count("**Đáp án nguồn:**") == 4,
          "worked solutions and Try It source answer labels")
    check("không thay thế bốn đáp án nguồn" in draft, "extra reasoning separately labeled")
    check("toàn mô-đun" in draft and "chủ yếu học mục" in draft, "second objective not claimed fulfilled")
    check(len(excerpt.find(CN + "metadata/" + MD + "abstract/" + CN + "list")) == 2,
          "two actual module objectives")
    for phrase in ("thị phần", "đã điều chỉnh lạm phát", "2000–2013", "2000–2003",
                   "24/3/2014", "cận dưới", "cận trên", "không phải số thực", "đồng thời"):
        check(phrase in draft, f"disclosed source/wording qualification: {phrase}")
    check("không chia cho 0" in draft and "x>0" in draft, "even root in denominator strictly positive")
    check("m50919" in draft and "m49299" in draft, "untranslated preface/chapter introduction explicit")
    # Each image-table row retains its exact inequality and interval, including endpoints.
    rows = [
        (r"$x>a$", r"$(a,\infty)$"), (r"$x<a$", r"$(-\infty,a)$"),
        (r"$x\ge a$", r"$[a,\infty)$"), (r"$x\le a$", r"$(-\infty,a]$"),
        (r"$a<x<b$", r"$(a,b)$"), (r"$a\le x<b$", r"$[a,b)$"),
        (r"$a<x\le b$", r"$(a,b]$"), (r"$a\le x\le b$", r"$[a,b]$"),
    ]
    for inequality, interval in rows:
        check(f"| {inequality} | {interval} |" in draft, "eight-row original image transcription")
    local_links = re.findall(r"\]\(#([^)]+)\)", draft)
    check(all(anchors.count(x) == 1 for x in local_links), "local figure/citation links resolve")
    cross = re.findall(r"\]\((A30-[^)]+)\)", draft)
    check(cross == ["A30-U000-module-guide.vi.html#vi-objectives"], "prior module link")
    target = (ROOT / "translation/A30-U000-module-guide.vi.md").read_text(encoding="utf-8")
    check(target.count("{#vi-objectives}") == 1, "prior module target draft anchor")
    image_refs = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check(len(image_refs) == 4 and all(len(alt) > 60 for alt, _ in image_refs), "four described original images")
    check([p for _, p in image_refs] == ["../assets/" + a["filename"] for a in ASSETS],
          "original image names/order retained")

    # Exact set projection, exact boundary arithmetic, and finite witnesses.
    pairs = [(2, 10), (3, 10), (4, 20), (5, 30), (6, 40)]
    check({x for x, _ in pairs} == {2, 3, 4, 5, 6}, "example1 domain projection")
    try_pairs = [(-5, 4), (0, 0), (5, -4), (10, -8), (15, -12)]
    check({x for x, _ in try_pairs} == {-5, 0, 5, 10, 15}, "TryIt1 domain projection")
    check(2 - 2 == 0 and 2 * F(1, 2) - 1 == 0, "fraction excluded values")
    check(F(-1 + 1, 2 - (-1)) == 0, "zero numerator is allowed")
    check(7 - 7 == 0 and 5 + 2 * F(-5, 2) == 0, "included square-root endpoints")
    samples = [F(-10), F(-5, 2), F(-1), F(0), F(1, 2), F(2), F(7), F(10)]
    for x in samples:
        check((2 - x != 0) == (x < 2 or x > 2), "fraction example membership")
        check((2 * x - 1 != 0) == (x < F(1, 2) or x > F(1, 2)), "TryIt3 membership")
        check((7 - x >= 0) == (x <= 7), "square-root example membership")
        check((5 + 2 * x >= 0) == (x >= F(-5, 2)), "TryIt4 membership")
        check((x >= 0 and x != 0) == (x > 0), "denominator root domain")
    for y in (F(-10), F(-2), F(-1), F(-1, 2), F(-1, 10)):
        x = 1 / (y * y)
        check(x > 0 and isclose(-1 / sqrt(float(x)), float(y), rel_tol=1e-12),
              "negative-range constructive sample")

    rights_file = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rights = {}
    if rights_file.is_file():
        with rights_file.open(encoding="utf-8-sig", newline="") as handle:
            rights = {r["asset_path"]: r for r in csv.DictReader(handle)}
    for asset in ASSETS:
        check(by_id[asset["media_id"]].find(CN + "image").get("src") ==
              "../../media/" + asset["filename"], "exact English source image reference")
        copies = [p for p in (ROOT / "assets" / asset["filename"],
                             ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"]) if p.is_file()]
        check(bool(copies) and all(p.stat().st_size == asset["bytes"] and
                                  sha256(p.read_bytes()).hexdigest() == asset["sha256"] for p in copies),
              "original source pixels/hash")
        if rights:
            row = rights["media/" + asset["filename"]]
            check(row["rights_component_id"] == asset["rights_component_id"] and
                  row["sha256"] == asset["sha256"] and row["admission"] == "admitted",
                  "inherited admitted asset row")

    spec = spec_from_file_location("u018_extract", ROOT / "tools/extract_domain_equations.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    for language, path in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if not path.is_file():
            continue
        original = ET.parse(path).getroot()
        selected = ET.fromstring(extractor.extract(path))
        check([n.get("id") for n in selected.iter() if n.get("id")] == ids, f"all actual source IDs {language}")
        check([canonical(n) for n in selected.iter(M + "math")] == [canonical(n) for n in math],
              f"all actual MathML unchanged {language}")
        check(original.find(CN + "content")[3].get("id") == extractor.STOP, f"exact next section {language}")
        if language == "en":
            check(extractor.extract(path) == source_text, "reproducible English source prefix")
            check(canonical(selected) == canonical(excerpt), "complete English prefix content")
        else:
            for asset in ASSETS:
                medium = selected.find(f".//{CN}media[@id='{asset['media_id']}']")
                check(medium.find(CN + "image").get("src") == asset["id_image_src"],
                      "Indonesian localized SVG difference recorded")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} mixed source/structure/asset and exact-boundary/finite-domain assertions")
