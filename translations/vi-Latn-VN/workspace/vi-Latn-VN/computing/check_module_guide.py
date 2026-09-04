"""Check U000 source objectives, partial-heading scope and17 navigation targets.

These are source/structure/link assertions, not mathematical proofs. The common
reader builder separately verifies links against the final registered HTML files.
"""
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
SOURCE_IDS = ["para-00001", "list-00001", "fs-id1165137737761"]
OBJECTIVES_EN = [
    "Determine whether a relation represents a function.",
    "Find the value of a function.",
    "Determine whether a function is one-to-one.",
    "Use the vertical line test to identify functions.",
    "Graph the functions listed in the library of functions.",
]
OBJECTIVES_VI = [
    "Xác định một quan hệ có biểu diễn một hàm số hay không.",
    "Tính giá trị của một hàm số.",
    "Xác định một hàm số có đơn ánh hay không.",
    "Dùng phép kiểm tra bằng đường thẳng đứng để nhận biết hàm số.",
    "Vẽ đồ thị các hàm số được liệt kê trong danh mục hàm số.",
]
TARGETS = [
    ("A30-U001-functions", "fs-id1165133394710"),
    ("A30-U002-function-notation", "fs-id1165134474160"),
    ("A30-U003-tables", "fs-id1165137804204"),
    ("A30-U004-input-output", "fs-id1165137503241"),
    ("A30-U005-one-to-one", "fs-id1165135422920"),
    ("A30-U006-graph-tests", "fs-id1165135435781"),
    ("A30-U007-toolkit-functions", "fs-id1165135545919"),
    ("A30-U008-key-summary", "fs-id1165135203679"),
    ("A30-U009-verbal-exercises", "fs-id1165137432988"),
    ("A30-U010-algebraic-classification", "fs-id1165134080937"),
    ("A30-U011-algebraic-evaluation", "fs-id1165134066606"),
    ("A30-U012-graphical-functions", "fs-id1165135664071"),
    ("A30-U013-graphical-injectivity", "fs-id1165135531627"),
    ("A30-U014-numeric-exercises", "fs-id1165135342204"),
    ("A30-U015-technology", "fs-id1165134373511"),
    ("A30-U016-real-world-applications", "fs-id1165135580349"),
    ("A30-U017-glossary", "fs-id1165137758543"),
]


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def tests():
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    text = (ROOT / "translation/A30-U000-module-guide.vi.md").read_text(encoding="utf-8")
    source_text = (ROOT / "sources/m49301-module-guide-source.cnxml").read_text(encoding="utf-8")
    source = ET.fromstring(source_text)
    check(text == unicodedata.normalize("NFC", text), "Vietnamese NFC")
    check(re.search(r"[^\n]\n$", text) is not None, "single final newline")
    ids = [node.get("id") for node in source.iter() if node.get("id")]
    check(ids == SOURCE_IDS, "exact three source IDs")
    anchors = re.findall(r"\{#([^}]+)\}", text)
    check(all(n == 1 for n in Counter(anchors).values()), "unique draft anchors")
    for identity in ids:
        check(anchors.count(identity) == 1, f"source anchor {identity}")
    metadata = source.find(CN + "metadata")
    check(source.find(CN + "title").text == "Functions and Function Notation", "English module title")
    check(metadata.find(MD + "title").text == source.find(CN + "title").text, "metadata title")
    check(metadata.find(MD + "content-id").text == "m49301", "source module identity")
    check(metadata.find(MD + "uuid").text == "11f4eacc-c348-4836-8c5b-747577d249ca", "source UUID")
    abstract = metadata.find(MD + "abstract")
    check(abstract.find(CN + "para").text == "In this section, you will:", "source objective introduction")
    check([n.text for n in abstract.find(CN + "list")] == OBJECTIVES_EN, "five exact English objectives")
    check(re.findall(r"^- (.+)$", text, re.M) == OBJECTIVES_VI, "five translated objectives in source order")
    section = source.find(CN + "content/" + CN + "section")
    check(section.get("class") == "section-exercises", "outer exercise class preserved")
    check(len(section) == 1 and section[0].tag == CN + "title", "only exercise heading selected")
    check(section[0].text == "Section Exercises", "source exercise heading")
    check("## Bài tập của mục {#fs-id1165137737761}" in text, "translated exercise heading")
    for tag in ("math", "exercise", "solution", "example", "figure", "media", "image", "table"):
        check(not any(n.tag.rsplit("}", 1)[-1] == tag for n in source.iter()), f"no source {tag}")
    check("{{math:" not in text and "![" not in text, "no math placeholders or images")
    check("Phần bổ sung — lộ trình đọc của bản dịch" in text and "Phần bổ sung — chỉ dẫn" in text,
          "navigation explicitly authored")
    check("không thêm bài tập hay đáp án" in text, "no claimed new exercises")
    check("không tự" in text and "lộ trình năm sách vẫn cần tiếp tục" in text, "no module/assignment completion claim")
    check("Hàm số và ký hiệu hàm số" in text and "Fungsi dan Notasi Fungsi" in text,
          "Vietnamese and Indonesian source titles identified")
    links = re.findall(r"\]\((A30-[^)]+)\)", text)
    check(links == [slug + ".vi.html#" + anchor for slug, anchor in TARGETS], "17 exact source-order reader links")
    registry = json.loads((ROOT / "units.json").read_text(encoding="utf-8"))
    for index, (slug, anchor) in enumerate(TARGETS, 1):
        unit = f"A30-U{index:03d}"
        check(slug.startswith(unit + "-"), f"pedagogical unit order {unit}")
        target = ROOT / "translation" / (slug + ".vi.md")
        check(target.is_file(), f"target draft exists {unit}")
        target_anchors = re.findall(r"\{#([^}]+)\}", target.read_text(encoding="utf-8"))
        check(target_anchors.count(anchor) == 1, f"exact target draft anchor {unit}")
        check(unit not in registry or registry[unit]["slug"] == slug,
              f"registry compatibility when integrated {unit}")

    spec = spec_from_file_location("u000_extract", ROOT / "tools/extract_module_guide.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    for language, path, title in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml", "Functions and Function Notation"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml", "Fungsi dan Notasi Fungsi"),
    ):
        if not path.is_file():
            continue
        original = ET.parse(path).getroot()
        original_metadata = original.find(CN + "metadata")
        check(original.find(CN + "title").text == title, f"actual original title {language}")
        check(original_metadata.find(MD + "title").text == title, f"actual metadata title {language}")
        original_abstract = original_metadata.find(MD + "abstract")
        check([n.get("id") for n in original_abstract] == SOURCE_IDS[:2], f"original abstract IDs {language}")
        check(len(original_abstract.find(CN + "list")) == 5, f"actual five objectives {language}")
        original_heading = original.find(f".//{CN}section[@id='{SOURCE_IDS[2]}']")
        check(original_heading.get("class") == "section-exercises", f"original outer section {language}")
        check(original_heading[1].get("id") == "fs-id1165137432988", f"heading stops before Verbal {language}")
        if language == "en":
            check(canonical(original_metadata) == canonical(metadata), "complete English metadata preserved")
            check(canonical(original_heading[0]) == canonical(section[0]), "English section title preserved")
            check(extractor.extract(path) == source_text, "reproducible exact excerpt")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure/navigation assertions; no mathematical proofs")
