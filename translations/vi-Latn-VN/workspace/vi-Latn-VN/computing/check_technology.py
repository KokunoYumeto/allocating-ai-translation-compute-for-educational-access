"""U015 preservation, exact range arithmetic and generated-plot checks.

Finite plot samples are illustrations, not proofs over continuous intervals.
The draft supplies the mathematical range reasoning. No images are rewritten.
"""
from collections import Counter
from decimal import Decimal as D
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose
from pathlib import Path
import csv
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SUPPLIED = {77, 79, 81, 83, 85, 87}
DOMAINS = ["[-0.1,0.1]", "[-10,10]", "[-100,100]", "[-0.1,0.1]",
           "[-10,10]", "[-100,100]", "[0,0.01]", "[0,100]", "[0,10,000]",
           "[-0.001,0.001]", "[-1000,1000]", "[-1,000,000,1,000,000]"]
SOURCE_RANGES = {77:"[0,100]", 79:"[-0.001,0.001]", 81:"[-1,000,000,1,000,000]",
                 83:"[0,10]", 85:"[-0.1,0.1]", 87:"[-100,100]"}
NUMERIC_MTEXT = ["\u00a010", "\u00a0100", "\u00a00", ".1", "\u00a00", ".001",
                 "\u00a010", "\u00a0100", "\u00a01,000,000", "\u00a00", ".01",
                 "\u00a0100", "\u00a010", "\u00a010,000", "0.001", "0.1",
                 "1000", "1,000,000", "\u00a0100"]
ASSETS = [
    {
        "number": 77,
        "filename": "CNX_Precalc_Figure_01_01_220-324e.jpg",
        "media_id": "fs-id1165133448050",
        "sha256": "8383a6cbd825880072ac8933cbb3c19123bbb25bdb9595968803c16baffd219c",
        "bytes": 53198,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:c77114362e4d387cfa528f7d"
    },
    {
        "number": 79,
        "filename": "CNX_Precalc_Figure_01_01_222-2e5d.jpg",
        "media_id": "fs-id1165135259631",
        "sha256": "406fb699b7007653a459d8a2f8d542942c3d0b0cbc6940781ac18698fbe29ebc",
        "bytes": 78484,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:b0b441a18c0ce72331cf4b74"
    },
    {
        "number": 81,
        "filename": "CNX_Precalc_Figure_01_01_224-c9b5.jpg",
        "media_id": "fs-id1165135434747",
        "sha256": "6664246a42170b808875835ad83bd56f94e5a94171bda891b567ab134e573f66",
        "bytes": 75496,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:3ee87f00c3a9819d9a3d9201"
    },
    {
        "number": 83,
        "filename": "CNX_Precalc_Figure_01_01_226-6e2a.jpg",
        "media_id": "fs-id1165137850247",
        "sha256": "4cefbe9473ffa08d890ee4248efc73285a2585602c20fcbe8603824801eb0f5c",
        "bytes": 53882,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:ab2f5329a8dd6126e1b1522b"
    },
    {
        "number": 85,
        "filename": "CNX_Precalc_Figure_01_01_228-c583.jpg",
        "media_id": "fs-id1165135407024",
        "sha256": "fa7de5f1eac0d68b5cd765423c4da82d2a0af5cdf16befb97c4845c6c3cf29b7",
        "bytes": 74785,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:4b49e4972cf4031d68f59af9"
    },
    {
        "number": 87,
        "filename": "CNX_Precalc_Figure_01_01_230-869c.jpg",
        "media_id": "fs-id1165135394245",
        "sha256": "33195af946d7e63564de9c12df7e6483015ff864574c23d299d22d7ba1d6f758",
        "bytes": 71776,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:25e69a14b234de25fdb7a54b"
    }
]


def load_module(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def compact_text(node):
    return re.sub(r"\s+", "", "".join(node.itertext())).replace("−", "-")


def tests():
    checks = 0

    def check(condition, label):
        nonlocal checks
        assert condition, label
        checks += 1

    extractor = load_module("u015_extractor", ROOT / "tools/extract_technology.py")
    plots = load_module("u015_plots", ROOT / "computing/plot_technology.py")
    source_path = ROOT / "sources/m49301-technology-source.cnxml"
    excerpt = source_path.read_text(encoding="utf-8")
    source = ET.fromstring(excerpt)
    section = source.find(f".//{CN}section")
    ids = [n.get("id") for n in source.iter() if n.get("id")]
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    exercises = list(source.iter(CN + "exercise"))
    draft = (ROOT / "translation/A30-U015-technology.vi.md").read_text(encoding="utf-8")
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(draft == unicodedata.normalize("NFC", draft), "NFC")
    check(len(ids) == len(set(ids)) == 59, "59 distinct source IDs")
    check(len(exercises) == 12, "12 source exercises")
    check([e.get("id") for e in exercises] == list(extractor.EXERCISE_IDS), "all12 source exercises in order")
    check([n.get("id") for n in section if n.tag == CN + "para"] == list(extractor.PROMPTS),
          "four retained shared function prompts")
    check(len(list(source.iter(CN + "solution"))) == 6, "six supplied range answers")
    check(len(list(source.iter(CN + "image"))) == 6, "six source answer images")
    check(not list(source.iter(CN + "table")), "no source tables")
    check(not list(source.iter(CN + "link")), "no source crossreferences")
    check("fs-id1165134272734" not in by_id, "later Real-World exercise is not in Technology")
    for identity in ids:
        check(anchors.count(identity) == 1, f"source anchor once {identity}")
    check(len(anchors) == len(set(anchors)), "no duplicate source or new anchors")
    links = re.findall(r"\]\(#([^)]+)\)", draft)
    check(len(links) == 24 and all(target in anchors for target in links), "12 answer and12 return links resolve")
    math = list(source.iter(M + "math"))
    check(len(math) == 22, "22 source MathML occurrences")
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft):
        candidates = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(candidates), f"valid math index {identity}:{index}")
        inserted.append(candidates[int(index)])
    check(Counter(map(id, math)) == Counter(map(id, inserted)), "all22 original formulas inserted once")
    check([n.text for n in source.iter(M + "mtext")] == NUMERIC_MTEXT,
          "all19 numeric mtext pieces including nonbreaking spaces and grouping commas unchanged")
    check(all(not re.search(r"[A-Za-z]", value) for value in NUMERIC_MTEXT),
          "numeric mtext needs no language substitution")
    for identity, kind in zip(extractor.PROMPTS, ("msup", "msup", "msqrt", "mroot")):
        check(len(list(by_id[identity].iter(M + kind))) == 1, f"exact shared function structure {identity}")
    for number, (exercise, domain) in enumerate(zip(exercises, DOMAINS), 76):
        para = exercise.find(f"{CN}problem/{CN}para")
        check(compact_text(para) == domain, f"source closed domain {number}")
        check(f"### Bài {number} {{#{exercise.get('id')}}}" in draft, f"source numbering {number}")
        solution = exercise.find(CN + "solution")
        check((solution is not None) == (number in SUPPLIED), f"answer availability {number}")
        answer_id = solution.get("id") if solution is not None else f"vi-sol-{number}"
        answer = re.search(rf"### Bài {number} — Lời giải \{{#{answer_id}\}}\n(.*?)(?=\n### |\n## )", draft, re.S)
        check(answer is not None, f"answer block {number}")
        block = answer.group(1)
        if solution is not None:
            check(compact_text(solution.find(CN + "para")) == SOURCE_RANGES[number], f"original answer range {number}")
            check("**Đáp án nguồn — tập giá trị:**" in block and "*Lời giải bổ sung:*" in block,
                  f"source answer separated from new reasoning {number}")
        else:
            check("**Đáp án và lời giải bổ sung — nguồn không kèm lời giải:**" in block,
                  f"new answer explicitly labeled {number}")
            check("**Đáp án nguồn" not in block, f"no invented source answer {number}")
        check(f"{{#vi-plot-{number}}}" in block and "*Đồ thị bổ sung — không phải ảnh nguồn." in block,
              f"new closed-endpoint plot clearly labeled {number}")
    check(draft.count("*Ghi chú hiệu chỉnh mô tả nguồn:*") == 2, "two disclosed English alternative-text errors")
    check("Sáu ảnh nguồn có mũi tên" in draft and "ngoài đoạn" in draft, "source arrows cannot extend closed domain")
    check("dấu chấm phẩy" in draft and "nhóm hàng nghìn" in draft, "number/interval separator explanation")
    check("10\\cdot10^5" in draft and "1\\,000\\,000" in draft, "million-axis scale clarified")
    image_links = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check(len(image_links) == 18, "six original images plus12new plots")
    check(all(len(alt) > 60 for alt, path in image_links), "detailed Vietnamese alternative text")
    check([path for alt, path in image_links if path.startswith("../assets/")] ==
          ["../assets/" + asset["filename"] for asset in ASSETS], "six source image names/order")

    # Exact arithmetic establishes endpoints/ranges independently of sampled pixels.
    for plot in plots.PLOTS:
        a, b = map(D, plot["domain"])
        c, d = map(D, plot["range"])
        check(a < b and c < d, f"ordered closed bounds {plot['number']}")
        if plot["kind"] == "square":
            check(a == -b and c == 0 and d == b * b, f"exact square range {plot['number']}")
        elif plot["kind"] == "cube":
            check(c == a ** 3 and d == b ** 3, f"exact cube range {plot['number']}")
        elif plot["kind"] == "sqrt":
            check(c >= 0 and c * c == a and d * d == b, f"exact principal-root range {plot['number']}")
        else:
            check(c ** 3 == a and d ** 3 == b, f"exact real cube-root range {plot['number']}")
        points = plots.samples(plot)
        check(len(points) == 321, f"sample count {plot['number']}")
        check(points[0][0] == float(a) and points[-1][0] == float(b), f"closed domain endpoints sampled {plot['number']}")
        expected_y = [float(d), float(d)] if plot["kind"] == "square" else [float(c), float(d)]
        check([points[0][1], points[-1][1]] == expected_y, f"correct filled endpoint coordinates {plot['number']}")
        check(all(float(a) - 1e-9 <= x <= float(b) + 1e-9 and float(c) - 1e-9 <= y <= float(d) + 1e-9
                  for x, y in points), f"sampled curve stays within declared domain/range {plot['number']}")
        if plot["kind"] in ("square", "cube"):
            exponent = 2 if plot["kind"] == "square" else 3
            condition = all(isclose(y, x ** exponent, rel_tol=1e-12, abs_tol=1e-12) for x, y in points)
        else:
            exponent = 2 if plot["kind"] == "sqrt" else 3
            condition = all(isclose(x, y ** exponent, rel_tol=1e-12, abs_tol=1e-12) for x, y in points)
        check(condition, f"finite samples satisfy plotted relation {plot['number']}")

    manifest = json.loads((plots.OUTPUT / "manifest.json").read_text(encoding="utf-8"))
    check(len(manifest["plots"]) == 12, "12 generated plot manifest rows")
    check(manifest["curve_arrows"] is False and manifest["filled_included_endpoints"] is True,
          "authored plot endpoint contract")
    check(manifest["independent_axis_scaling"] is True, "axis scaling declared")
    for plot, row in zip(plots.PLOTS, manifest["plots"]):
        check(all(row[key] == plot[key] for key in ("number", "kind", "domain", "range", "formula")),
              f"manifest function/domain/range {plot['number']}")
        path = plots.OUTPUT / row["filename"]
        check(path.stat().st_size == row["bytes"] and sha256(path.read_bytes()).hexdigest() == row["sha256"],
              f"generated plot exact hash {plot['number']}")
        check(("../computing/generated-A30-U015/" + row["filename"]) in [p for alt, p in image_links],
              f"new plot linked in draft {plot['number']}")
    # Rendering uses a pinned font hash/version; --check is a separate exact-byte
    # reproduction test and is not needed on hosts without that original font.

    rights_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rights = {}
    if rights_path.exists():
        with rights_path.open(encoding="utf-8-sig", newline="") as handle:
            rights = {r["asset_path"]: r for r in csv.DictReader(handle)}
    for asset in ASSETS:
        check(by_id[asset["media_id"]].find(CN + "image").get("src") == "../../media/" + asset["filename"],
              "source asset reference unchanged")
        paths = [p for p in (ROOT / "assets" / asset["filename"],
                            ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"]) if p.is_file()]
        check(bool(paths) and all(p.stat().st_size == asset["bytes"] and sha256(p.read_bytes()).hexdigest() == asset["sha256"]
                                  for p in paths), f"unaltered original pixels {asset['filename']}")
        if rights:
            row = rights["media/" + asset["filename"]]
            check(row["rights_component_id"] == asset["rights_component_id"] and row["admission"] == "admitted"
                  and row["sha256"] == asset["sha256"] and row["license_id"] == "CC-BY-NC-SA-4.0",
                  "inherited admitted row")
    for language, path in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml"),
    ):
        if not path.exists():
            continue
        original = ET.parse(path)
        orig_section = original.find(f".//{CN}section[@id='{extractor.SECTION}']")
        parent = next(n for n in original.iter() if orig_section in list(n))
        check(list(parent)[list(parent).index(orig_section) + 1].get("id") == extractor.STOP, f"next category {language}")
        check([n.get("id") for n in orig_section.iter() if n.get("id")] == ids, f"all original IDs {language}")
        check([canonical(n) for n in orig_section.iter(M + "math")] == [canonical(n) for n in math],
              f"all source MathML unchanged {language}")
        check([n.get("src") for n in orig_section.iter(CN + "image")] ==
              ["../../media/" + a["filename"] for a in ASSETS], f"all source images unchanged {language}")
        if language == "en":
            check(canonical(orig_section) == canonical(section), "full English section preserved")
            check(extractor.extract(path) == excerpt, "exact reproducible excerpt")
    return checks


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure/asset checks and exact-range/finite-plot assertions")
