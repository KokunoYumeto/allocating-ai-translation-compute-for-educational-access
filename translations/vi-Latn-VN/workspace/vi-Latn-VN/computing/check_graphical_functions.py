"""U012 structural/source checks and finite witnesses read from source graphs.

The JPEGs are checked against locked hashes; visual interpretations are recorded
in provenance/U012-source-review.json. Finite points do not prove all-curve tests.
No image is created, changed, fetched, or copied by this module.
"""
from collections import Counter
import csv
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
NON_FUNCTIONS = {41, 44, 46, 48, 50}
SUPPLIED = {41, 43, 45, 47, 49, 51, 53}
ASSETS = [
    {
        "number": 40,
        "exercise_id": "fs-id1165135455987",
        "media_id": "fs-id1165135455994",
        "filename": "CNX_Precalc_Figure_01_01_201-5fd2.jpg",
        "sha256": "719973649f86f774aecea4456acf55dac06838701eea375de8c79cb9ae4ce74e",
        "bytes": 48512,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:c91a2253096374acb6a0a738"
    },
    {
        "number": 41,
        "exercise_id": "fs-id1165137527641",
        "media_id": "fs-id1165137847091",
        "filename": "CNX_Precalc_Figure_01_01_202-c11d.jpg",
        "sha256": "ce4b981213750424ced1a09bb3365dec5ddaf6968b4bf8c2375d4fb0f165199a",
        "bytes": 46935,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:ab9116ecdd6c3a7a031b3056"
    },
    {
        "number": 42,
        "exercise_id": "fs-id1165135332512",
        "media_id": "fs-id1165133336405",
        "filename": "CNX_Precalc_Figure_01_01_203-401d.jpg",
        "sha256": "d088a964d103efd1a1053fae4692d9be352bb5fa0f217856f6c596decee9c4be",
        "bytes": 57371,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:fafa3dacd8c32f9bcd0d08ff"
    },
    {
        "number": 43,
        "exercise_id": "fs-id1165137742393",
        "media_id": "fs-id1165137597394",
        "filename": "CNX_Precalc_Figure_01_01_204-3920.jpg",
        "sha256": "c886083ddf93c4badf8826b8a53e81c71402deac22a930c1970ad1cdce953bd2",
        "bytes": 42679,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:1abee03f72e0b0403fda7ce8"
    },
    {
        "number": 44,
        "exercise_id": "fs-id1165135386379",
        "media_id": "fs-id1165135386387",
        "filename": "CNX_Precalc_Figure_01_01_205-9b65.jpg",
        "sha256": "d1f9bc4a5ee99aae143fea9a6576f2dc96fa3df3de211a116abed3293b3133d0",
        "bytes": 38378,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:b65976ab388475b8e4b5b668"
    },
    {
        "number": 45,
        "exercise_id": "fs-id1165137749974",
        "media_id": "fs-id1165137439470",
        "filename": "CNX_Precalc_Figure_01_01_206-a4e5.jpg",
        "sha256": "d6d1665cbdeac392c3756ae35a1da14e5794221084d73d04079be3dc2bcff4f4",
        "bytes": 48267,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:db3da2766d0361ac1d4d2fe6"
    },
    {
        "number": 46,
        "exercise_id": "fs-id1165137399704",
        "media_id": "fs-id1165135704896",
        "filename": "CNX_Precalc_Figure_01_01_207-0288.jpg",
        "sha256": "0478ac299518af96092d33fd2788f9beef8cc558a8b9167170d2aa5e05078f7b",
        "bytes": 48128,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:4a2af830cc1a4d47187194b2"
    },
    {
        "number": 47,
        "exercise_id": "fs-id1165137883764",
        "media_id": "fs-id1165137883773",
        "filename": "CNX_Precalc_Figure_01_01_208-492c.jpg",
        "sha256": "fc873f6a85eb6dbe1046388ad60d98ebb4b167ac47d44ba3b8d382e6fe4af980",
        "bytes": 38420,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:c7e6bfcc910026a928c8fb68"
    },
    {
        "number": 48,
        "exercise_id": "fs-id1165134497159",
        "media_id": "fs-id1165134497168",
        "filename": "CNX_Precalc_Figure_01_01_209-6bc3.jpg",
        "sha256": "c4569ca281b4e1913198cac4af16917f2711e54cf63a626abfc46d93fa619f3e",
        "bytes": 58328,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:5decdbe6573eaa111958c507"
    },
    {
        "number": 49,
        "exercise_id": "fs-id1165135496435",
        "media_id": "fs-id1165134234204",
        "filename": "CNX_Precalc_Figure_01_01_210-1a0b.jpg",
        "sha256": "39b4485972b8a1385bdc6f5793dff6c8f819597dffdd7e666c7ded0ca39a46a6",
        "bytes": 44168,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:738606a73f20dda93e2a5666"
    },
    {
        "number": 50,
        "exercise_id": "fs-id1165137911653",
        "media_id": "fs-id1165137786191",
        "filename": "CNX_Precalc_Figure_01_01_211-3512.jpg",
        "sha256": "237e9faf8217e51500d82ab1e13ecfe40a5cf91a03dd83e20459edefda12d74f",
        "bytes": 40754,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:a6794eb3cfeb264ab9ee53d7"
    },
    {
        "number": 51,
        "exercise_id": "fs-id1165135593325",
        "media_id": "fs-id1165135593333",
        "filename": "CNX_Precalc_Figure_01_01_212-3015.jpg",
        "sha256": "b20fec60b70fee87edc494adc799a16150b7a85ee853c4ff33fbb1cd87bd6f69",
        "bytes": 41867,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:ea3d54ae67de79e4618b6edd"
    },
    {
        "number": 52,
        "exercise_id": "fs-id1165134240968",
        "media_id": "fs-id1165137834413",
        "filename": "CNX_Precalc_Figure_01_01_213-fd68.jpg",
        "sha256": "a91c5d5b0e1d23d2142a0ff13841daaee917e1bfe029af3d27c2860eb63d8d3e",
        "bytes": 53523,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:48745ed549878cd349ccfcaa"
    },
    {
        "number": 53,
        "exercise_id": "fs-id1165135632092",
        "media_id": "fs-id1165135567425",
        "filename": "CNX_Precalc_Figure_01_01_214-4087.jpg",
        "sha256": "622e06725edb3dfc6afd2e950b73777d7758c3c4ae625f481159f2593f7b8f33",
        "bytes": 69055,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:5347e20c5a088dbfc92a389f"
    },
    {
        "number": 54,
        "exercise_id": "fs-id1165134325868",
        "media_id": "fs-id1165135575950",
        "filename": "CNX_Precalc_Figure_01_01_215-571f.jpg",
        "sha256": "2e6384cdd5a6d31a976c1f03bfdda6c4ca233b386129b3e4dff67fb01fbcf9ff",
        "bytes": 76007,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:2f700ab5fae397f614c6262b"
    }
]

def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def values(pairs, x):
    return {y for first, y in pairs if first == x}


def inputs(pairs, y):
    return {x for x, second in pairs if second == y}


def tests():
    count = 0

    def check(condition, message):
        nonlocal count
        assert condition, message
        count += 1

    spec = spec_from_file_location("u012_extractor", ROOT / "tools/extract_graphical_functions.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    path = ROOT / "sources/m49301-graphical-functions-source.cnxml"
    excerpt = path.read_text(encoding="utf-8")
    source = ET.fromstring(excerpt)
    section = source.find(f".//{CN}section")
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    source_ids = [n.get("id") for n in source.iter() if n.get("id")]
    exercises = list(source.iter(CN + "exercise"))
    markdown = (ROOT / "translation/A30-U012-graphical-functions.vi.md").read_text(encoding="utf-8")
    anchors = re.findall(r"\{#([^}]+)\}", markdown)
    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    check(len(source_ids) == len(set(source_ids)) == 67, "67 distinct source IDs")
    check(len(exercises) == 15, "15 exercises, including Figure215 exercise")
    check([e.get("id") for e in exercises] == list(extractor.EXERCISE_IDS), "exact exercise order")
    check(exercises[-1].get("id") == "fs-id1165134325868", "corrected fifteenth endpoint")
    check(exercises[-2].get("id") == "fs-id1165135632092", "old map endpoint is only fourteenth")
    check([n.get("id") for n in section if n.tag == CN + "para"] == [extractor.START_PROMPT],
          "one shared vertical-test instruction")
    check(extractor.STOP not in by_id, "stop before horizontal-test shared prompt")
    check(len(list(source.iter(CN + "solution"))) == 7, "seven supplied answers")
    check(len(list(source.iter(CN + "media"))) == 15, "15 source media")
    check(len(list(source.iter(CN + "image"))) == 15, "15 source JPEGs")
    check(len(list(source.iter(CN + "list"))) == 4, "three two-part problems and one source answer list")
    check(len(list(source.iter(CN + "item"))) == 8, "eight source list parts")
    check(not list(source.iter(CN + "table")), "no source tables")
    check(not list(source.iter(CN + "link")), "no original crossreferences")
    for identity in source_ids:
        check(anchors.count(identity) == 1, f"one explicit source anchor {identity}")
    check(len(anchors) == len(set(anchors)), "no duplicate authored/source anchors")
    local = re.findall(r"\]\(#([^)]+)\)", markdown)
    check(len(local) == 30, "15 answer links and15 return links")
    check(all(target in anchors for target in local), "all local links resolve")

    math = list(source.iter(M + "math"))
    check(len(math) == 9, "six problem and three answer MathML expressions")
    rendered = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        candidates = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(candidates), f"valid MathML index {identity}:{index}")
        rendered.append(candidates[int(index)])
    check(Counter(map(id, rendered)) == Counter(map(id, math)), "all nine source math occurrences exactly once")
    check(not list(source.iter(M + "mtext")), "no MathML text replacements needed")
    expected_numbers = {
        "fs-id1165134054032": ["−1", "3."],
        "fs-id1165137861994": ["0", "−3."],
        "fs-id1165134325875": ["4", "1."],
        "eip-idm666464064": ["0", "1", "3", "2", "2"],
    }
    for identity, expected in expected_numbers.items():
        check([n.text for n in by_id[identity].iter(M + "mn")] == expected, f"source numbers {identity}")
        block = re.search(r"::: \{#" + identity + r"\}\n(.*?)\n:::", markdown, re.S)
        check(block is not None and block.group(1).count("ⓐ") == 1 and block.group(1).count("ⓑ") == 1,
              f"source part labels retained {identity}")

    image_links = re.findall(r"!\[([^\]]+)\]\(\.\./assets/([^)]+)\)", markdown)
    check([name for alt, name in image_links] == [a["filename"] for a in ASSETS], "all15 image links in source order")
    check(all(len(alt) > 50 for alt, name in image_links), "nonempty detailed Vietnamese alternative text")
    for number, exercise in enumerate(exercises, 40):
        check(f"### Bài {number} {{#{exercise.get('id')}}}" in markdown, f"visible source number {number}")
        prompt = re.search(rf"### Bài {number} \{{#{exercise.get('id')}\}}\n(.*?)(?=\n### |\n## )", markdown, re.S)
        check(prompt is not None and "*Mô tả hình bổ sung:*" in prompt.group(1), f"accessible graph description {number}")
        solution = exercise.find(CN + "solution")
        check((solution is not None) == (number in SUPPLIED), f"correct source answer availability {number}")
        answer_id = solution.get("id") if solution is not None else f"vi-sol-{number}"
        answer = re.search(rf"### Bài {number} — Lời giải \{{#{answer_id}\}}\n(.*?)(?=\n### |\n## )", markdown, re.S)
        check(answer is not None, f"answer block {number}")
        block = answer.group(1)
        if solution is not None:
            check("**Đáp án nguồn:**" in block, f"supplied answer label {number}")
            check("*Lời giải bổ sung:*" in block, f"added reasoning distinguished {number}")
            if number < 52:
                expected = "not a function" if number in NON_FUNCTIONS else "function"
                check(" ".join("".join(solution.itertext()).split()) == expected, f"source classification {number}")
                vietnamese = "Không phải là hàm số." if number in NON_FUNCTIONS else "Là hàm số."
                check(f"**Đáp án nguồn:** {vietnamese}" in block, f"translated classification {number}")
        else:
            check("**Đáp án và lời giải bổ sung — nguồn không kèm lời giải:**" in block,
                  f"clearly authored missing-source answer {number}")
            check("**Đáp án nguồn:**" not in block, f"no invented source answer {number}")
            if number < 52:
                label = "**Không phải là hàm số." if number in NON_FUNCTIONS else "**Là hàm số."
                check(label in block, f"authored classification {number}")
    check("Ghi chú hiệu chỉnh mô tả nguồn" in markdown and markdown.count("*Ghi chú hiệu chỉnh mô tả nguồn:*") == 2,
          "two disclosed source alternative-text corrections")
    check("đường tiệm cận, không phải" in markdown, "Figure203 asymptote excluded from relation")
    check("x>0" in markdown and "x<2" in markdown, "Figure207 open-ray restrictions")
    check("7 bài" in markdown and "8 bài" in markdown, "source versus authored answer counts disclosed")

    # These are inherited component-admission rows, not a new supply audit.
    rights_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rights = {}
    if rights_path.is_file():
        with rights_path.open(encoding="utf-8-sig", newline="") as handle:
            rights = {row["asset_path"]: row for row in csv.DictReader(handle)}
    for asset in ASSETS:
        image_node = by_id[asset["media_id"]].find(CN + "image")
        check(image_node.get("src") == "../../media/" + asset["filename"], "exact source filename")
        paths = [p for p in (
            ROOT / "assets" / asset["filename"],
            ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"],
        ) if p.is_file()]
        check(bool(paths), "at least one exact original/admitted local image available")
        check(all(p.stat().st_size == asset["bytes"] and sha256(p.read_bytes()).hexdigest() == asset["sha256"] for p in paths),
              f"unchanged original image bytes {asset['filename']}")
        if rights:
            row = rights["media/" + asset["filename"]]
            check(row["rights_component_id"] == asset["rights_component_id"] and row["admission"] == "admitted"
                  and row["license_id"] == "CC-BY-NC-SA-4.0" and row["sha256"] == asset["sha256"]
                  and int(row["bytes"]) == asset["bytes"], f"inherited admitted row {asset['filename']}")

    for language, original_path in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml"),
    ):
        if not original_path.is_file():
            continue
        original = ET.parse(original_path)
        parent = original.find(f".//{CN}section[@id='{extractor.PARENT}']")
        selected = []
        for node in parent:
            if node.get("id") == extractor.STOP:
                break
            selected.append(node)
        check(list(parent)[len(selected)].get("id") == extractor.STOP, f"actual next shared prompt {language}")
        check([n.get("id") for n in selected if n.tag == CN + "exercise"] == list(extractor.EXERCISE_IDS),
              f"original15 exercise sequence {language}")
        originals_ids = [parent.get("id")] + [n.get("id") for item in selected for n in item.iter() if n.get("id")]
        check(originals_ids == source_ids, f"original source IDs {language}")
        original_math = [n for item in selected for n in item.iter(M + "math")]
        check([canonical(n) for n in original_math] == [canonical(n) for n in math], f"unaltered source MathML {language}")
        check([n.get("src") for item in selected for n in item.iter(CN + "image")] ==
              ["../../media/" + a["filename"] for a in ASSETS], f"original15 image references {language}")
        if language == "en":
            check([canonical(n) for n in selected] == [canonical(n) for n in section], "English content and attributes preserved")
            check(extractor.extract(original_path) == excerpt, "exact reproducible source excerpt")
        else:
            solutions = [n for item in selected for n in item.iter(CN + "solution")]
            check([" ".join("".join(n.itertext()).split()) for n in solutions[:6]] ==
                  ["bukan fungsi", "fungsi", "fungsi", "fungsi", "fungsi", "fungsi"],
                  "Indonesian classifications agree")
    # Finite graph witnesses manually transcribed from the verified source pixels.
    ray_outputs = lambda x: ({3} if x > 0 else set()) | ({-3} if x < 2 else set())
    check(ray_outputs(1) == {-3, 3}, "Figure207 two outputs at x1")
    check(ray_outputs(0) == {-3}, "Figure207 open upper endpoint")
    check(ray_outputs(2) == {3}, "Figure207 open lower endpoint")
    check(values([(1, 1), (1, -1)], 1) == {-1, 1}, "Figure209 crossing-line counterexample")
    check(values([(-2, 0), (-2, 4)], -2) == {0, 4}, "Figure211 vertical diameter counterexample")
    graph213 = [(-2, 0), (-1, 1), (7, 3)]
    graph214 = [(-2, -3), (0, 1), (2, -3)]
    graph215 = [(-6, 1), (-3, 4), (0, 1), (4, -3)]
    check(values(graph213, -1) == {1}, "Figure213 value")
    check(inputs(graph213, 3) == {7}, "Figure213 recorded input at height3")
    check(values(graph214, 0) == {1}, "Figure214 source value")
    check(inputs(graph214, -3) == {-2, 2}, "Figure214 source pair of inputs")
    check(values(graph215, 4) == {-3}, "Figure215 value")
    check(inputs(graph215, 1) == {-6, 0}, "Figure215 both recorded inputs")
    check(all(4 - abs(x + 3) == y for x, y in graph215), "Figure215 straight-ray geometry consistency")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure/asset/answer-label and finite graph-witness assertions")
