"""U020 bounded graph-reading source, endpoint, unit, and finite checks.

Default checks use the committed excerpt/draft and five original images. Before
root copies assets, the exact pinned downloads are accepted as a read-only
fallback. --originals additionally compares both complete pinned source modules.
No script output is a proof of an infinite domain or a precise digitization.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137653855"
STOP = "fs-id1165134384565"
EXCERPT_SHA = "d0faba22a5e9fb22a7e4b40122586c3b3d46625f5718641c1e81086ca145a8ee"
ORIGINALS = (
    ("en", "downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("id", "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)
ASSETS = [
    {
        "media_id": "fs-id1165137432156",
        "filename": "CNX_Precalc_Figure_01_02_006-aec6.jpg",
        "sha256": "7b36ccb52216a93542f265707a3b7a8ab6ff684c6e84248720fb51326a8cf439",
        "bytes": 136018,
        "en_src": "../../media/CNX_Precalc_Figure_01_02_006-aec6.jpg",
        "id_src": "../../media/CNX_Precalc_Figure_01_02_006-aec6.jpg"
    },
    {
        "media_id": "fs-id1165137805567",
        "filename": "CNX_Precalc_Figure_01_02_007-940d.jpg",
        "sha256": "d757bef07a7f3684cab2978f3f280309474b46d3021cef93d53ef3589a445544",
        "bytes": 81380,
        "en_src": "../../media/CNX_Precalc_Figure_01_02_007-940d.jpg",
        "id_src": "../../media/CNX_Precalc_Figure_01_02_007-940d.jpg"
    },
    {
        "media_id": "fs-id1165137937577",
        "filename": "CNX_Precalc_Figure_01_02_008_new.jpg",
        "sha256": "6497d4f7abc59e0c8d9efa176770b493d4cb32c609888fe98220c5b5434abea6",
        "bytes": 64337,
        "en_src": "../../media/CNX_Precalc_Figure_01_02_008_new.jpg",
        "id_src": "../../media/CNX_Precalc_Figure_01_02_008_new.jpg"
    },
    {
        "media_id": "fs-id1165135186977",
        "filename": "CNX_Precalc_Figure_01_02_009-e7be.jpg",
        "sha256": "e557f2133b64956559080a5853aec777bef0b138922b61016a85fbe5ab81bb56",
        "bytes": 107313,
        "en_src": "../../media/CNX_Precalc_Figure_01_02_009-e7be.jpg",
        "id_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_009-id.svg"
    },
    {
        "media_id": "fs-id1165137827275",
        "filename": "CNX_Precalc_Figure_01_02_010-d86a.jpg",
        "sha256": "0c6a3b10c890d9524a25313ebc2de024d2957d49695db038e417b33548b844be",
        "bytes": 96459,
        "en_src": "../../media/CNX_Precalc_Figure_01_02_010-d86a.jpg",
        "id_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_010-id.svg"
    }
]
SOURCE_IDS = [
    "fs-id1165137653855",
    "fs-id1165135161404",
    "Figure_01_02_006",
    "fs-id1165137432156",
    "fs-id1165137597994",
    "Example_01_02_06",
    "fs-id1165137561401",
    "fs-id1165137599824",
    "fs-id1165135187604",
    "Figure_01_02_007",
    "fs-id1165137805567",
    "fs-id1165137575085",
    "fs-id1165137768165",
    "fs-id1165131968670",
    "Figure_01_02_008",
    "fs-id1165137937577",
    "Example_01_02_07",
    "fs-id1165134182686",
    "fs-id1165137461643",
    "fs-id1165137443324",
    "Figure_01_02_009",
    "fs-id1165135186977",
    "fs-id1165135445728",
    "fs-id1165137444311",
    "fs-id1165137476085",
    "fs-id1165137747998",
    "fs-id1165135545972",
    "ti_01_02_04",
    "fs-id1165137644581",
    "fs-id1165137644582",
    "Figure_01_02_010",
    "fs-id1165137827275",
    "fs-id1165137705252",
    "fs-id1165134079741",
    "fs-id1165137434590",
    "fs-id1165137812796",
    "fs-id1165137433394"
]
NUMERIC = {
    "fs-id1165137476085": [
        "1973",
        "2008",
        "180",
        "2010."
    ],
    "fs-id1165137597994": [
        "−5",
        "−5",
        "5",
        "5"
    ],
    "fs-id1165131968670": [
        "4",
        "0"
    ],
    "fs-id1165137768165": [
        "3",
        "1"
    ]
}
COUNTS = {}


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def tests(originals=False):
    counts = {"source_structure_asset": 0, "finite_endpoint_units": 0,
              "optional_original_source": 0}

    def check(condition, label, category="source_structure_asset"):
        assert condition, label
        counts[category] += 1

    excerpt_path = ROOT / "sources/m49304-domain-range-graphs-source.cnxml"
    data = excerpt_path.read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned excerpt bytes")
    excerpt = ET.fromstring(data)
    draft = (ROOT / "translation/A30-U020-domain-range-graphs.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    ids = [node.get("id") for node in excerpt.iter() if node.get("id")]
    by_id = {node.get("id"): node for node in excerpt.iter() if node.get("id")}
    check(ids == SOURCE_IDS and len(ids) == len(set(ids)) == 37, "37 ordered module-local source IDs")
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(all(n == 1 for n in Counter(anchors).values()), "unique draft anchors")
    for identity in ids:
        check(anchors.count(identity) == 1, f"source anchor {identity}")
    section = excerpt.find(CN + "content/" + CN + "section")
    check(section.get("id") == SECTION, "one selected source section")
    check(section[-1].get("id") == "fs-id1165137434590", "complete final Q&A")
    check(section[-1][-1].get("id") == "fs-id1165137433394", "complete final answer paragraph")
    check(STOP not in ids, "following toolkit section excluded")
    check([node.get("id") for node in section.iter(CN + "example")] ==
          ["Example_01_02_06", "Example_01_02_07"], "Examples6–7 in source order")
    check([node.get("id") for node in section.iter(CN + "exercise")] ==
          ["fs-id1165137561401", "fs-id1165134182686", "ti_01_02_04"],
          "two example exercises plus one Try It")
    check([node.get("id") for node in section.iter(CN + "solution")] ==
          ["fs-id1165137575085", "fs-id1165137444311", "fs-id1165137705252"],
          "all three source-supplied solutions retained")
    check(draft.count("**Lời giải nguồn.**") == 2, "two worked-source solution labels")
    check(draft.count("**Đáp án nguồn — giữ nguyên để đối chiếu:**") == 1,
          "one retained-source Try It answer label")
    check(not list(section.iter(CN + "table")), "no source table invented")
    check(len(list(section.iter(CN + "note"))) == 2, "Try It and Q&A only")

    math = list(excerpt.iter(M + "math"))
    references = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(references) == len(math) == 13, "13 source MathML occurrences")
    captured = [list(by_id[identity].iter(M + "math"))[int(index)]
                for identity, index in references]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "each source formula referenced exactly once")
    check(not list(excerpt.iter(M + "mtext")), "no MathML text replacement required")
    for identity, numbers in NUMERIC.items():
        check([node.text for node in by_id[identity].iter(M + "mn")] == numbers,
              f"preserved source number tokens {identity}")
    supplied_population = "".join(by_id["fs-id1165134079741"].itertext())
    check(re.findall(r"\d+", supplied_population) ==
          ["1950", "2002", "47", "000", "000", "89", "000", "000"],
          "source population answer digits retained, including disputed2002")
    check(r"$[1950,2002]$" in draft and r"$[47\,000\,000,89\,000\,000]$" in draft,
          "same source-answer values displayed in Vietnamese")
    check(r"$[1950,2000]$" in draft and "Ghi chú hiệu chỉnh — phần bổ sung" in draft,
          "graph-based corrected endpoint separately disclosed")
    check("46–47 triệu" in draft and r"$[47,89]$" in draft,
          "population image reading not falsely exact")
    for phrase in ("không phải tổng dân số", "nghìn thùng", "không phải 2010 thùng",
                   "không phải các", "không phải\nnhững điểm bổ sung",
                   "sắp cận theo giá trị số", "một công thức chính xác",
                   "phạm vi công cộng"):
        check(phrase in draft, "source interpretation/attribution qualification: " + phrase)
    check(r"$(0,0)$" in draft and "giá trị\n$y=0$ vẫn được nhận" in draft,
          "open point does not erase an output attained elsewhere")
    check(r"$x=y^3$" in draft and r"$\sqrt[3]{x}=y$" in draft,
          "constructive cube-root range argument present")
    check("không thay việc đọc đồ thị" in draft and "số đọc từ ảnh" in draft,
          "computing and image precision limits explicit")

    local_links = re.findall(r"\]\(#([^)]+)\)", draft)
    source_links = [node.get("target-id") for node in section.iter(CN + "link")]
    check(source_links == [f"Figure_01_02_00{i}" for i in range(6, 10)] +
          ["Figure_01_02_010"], "five source figure crossreferences")
    check(all(target in local_links for target in source_links), "all five source links retained")
    check(local_links == source_links[:4] + ["fs-id1165135445728"] + source_links[4:],
          "five figure links plus one source-footnote link in order")
    for target in local_links:
        check(anchors.count(target) == 1, f"local target {target}")
    check(not re.findall(r"\]\((A30-[^)]+\.html[^)]*)\)", draft), "no new cross-reader dependencies")
    eia_url = "http://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=MCRFPAK2&f=A"
    check(eia_url in draft, "original EIA attribution URL retained")
    check("U.S. Energy Information" in draft and "Administration" in draft, "EIA credit retained")

    image_refs = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check(len(image_refs) == 5 and all(len(alt) > 70 for alt, _ in image_refs),
          "five accessible original-image descriptions")
    check([p for _, p in image_refs] == ["../assets/" + a["filename"] for a in ASSETS],
          "original filenames and figure order retained")
    for asset in ASSETS:
        node = by_id[asset["media_id"]].find(CN + "image")
        check(node.get("src") == asset["en_src"], "source image reference " + asset["filename"])
        candidates = [ROOT / "assets" / asset["filename"],
                      ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"]]
        existing = [path for path in candidates if path.is_file()]
        check(bool(existing), "committed asset or pinned original exists " + asset["filename"])
        check(all(path.stat().st_size == asset["bytes"] and
                  sha256(path.read_bytes()).hexdigest() == asset["sha256"] for path in existing),
              "original pixels/bytes preserved " + asset["filename"])

    # Exact endpoint membership and unit conversions; not graph digitization.
    category = "finite_endpoint_units"
    for x, expected in [(-6, False), (-5, True), (-3, True), (0, True), (100, True)]:
        check((x >= -5) == expected, "Figure6 domain finite membership", category)
    for y, expected in [(-100, True), (0, True), (5, True), (6, False)]:
        check((y <= 5) == expected, "Figure6 range finite membership", category)
    for x, expected in [(-4, False), (-3, False), (-2, True), (0, True), (1, True), (2, False)]:
        check((-3 < x <= 1) == expected, "Example6 domain endpoints", category)
    for y, expected in [(-5, False), (-4, True), (-1, True), (0, True), (1, False)]:
        check((-4 <= y <= 0) == expected, "Example6 range endpoints", category)
    included_points = {(-2, -4), (0, 0), (1, -4)}
    check((-3, 0) not in included_points and any(y == 0 for _, y in included_points),
          "omitted point with separately attained output0", category)
    check({y for _, y in included_points} == {-4, 0}, "included range endpoint witnesses", category)
    for millions, people in [(47, 47000000), (89, 89000000)]:
        check(millions * 1000000 == people, "population source units exact conversion", category)
    for thousands, barrels in [(180, 180000), (2010, 2010000)]:
        check(thousands * 1000 == barrels, "oil source units exact conversion", category)
    for y, x in [(F(-2), F(-8)), (F(-1, 2), F(-1, 8)), (F(0), F(0)),
                 (F(1, 2), F(1, 8)), (F(3), F(27))]:
        check(y ** 3 == x, "finite exact witnesses for cube-root converse x=y^3", category)

    if originals:
        spec = spec_from_file_location("u020_extract", ROOT / "tools/extract_domain_range_graphs.py")
        extractor = module_from_spec(spec)
        spec.loader.exec_module(extractor)
        for language, relative, expected_sha in ORIGINALS:
            path = ROOT.parent / relative
            category = "optional_original_source"
            check(path.is_file(), "actual source present " + language, category)
            check(sha256(path.read_bytes()).hexdigest() == expected_sha,
                  "pinned actual complete module " + language, category)
            selected_text = extractor.extract(path)
            selected = ET.fromstring(selected_text)
            check([node.get("id") for node in selected.iter() if node.get("id")] == ids,
                  "all actual selected IDs/order " + language, category)
            check([canonical(node) for node in selected.iter(M + "math")] ==
                  [canonical(node) for node in math], "all actual MathML " + language, category)
            actual_section = selected.find(CN + "content/" + CN + "section")
            check(actual_section[-1].get("id") == "fs-id1165137434590",
                  "final source Q&A intact " + language, category)
            if language == "en":
                check(selected_text == data.decode("utf-8"), "exact reproducible English excerpt", category)
                check(canonical(selected) == canonical(excerpt), "complete selected English content", category)
            else:
                for asset in ASSETS:
                    medium = selected.find(f".//{CN}media[@id='{asset['media_id']}']")
                    check(medium.find(CN + "image").get("src") == asset["id_src"],
                          "actual ID JPEG/SVG path " + asset["filename"], category)
                population = selected.find(f".//{CN}para[@id='fs-id1165134079741']")
                check(re.findall(r"\d+", "".join(population.itertext())) ==
                      re.findall(r"\d+", supplied_population),
                      "same disputed source population answer in ID", category)
    COUNTS.clear()
    COUNTS.update(counts)
    return sum(counts.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", action="store_true")
    total = tests(parser.parse_args().originals)
    print(f"PASS: {total} mixed assertions; breakdown {COUNTS}")
