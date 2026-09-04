"""U008 source/table/cross-reader checks.

These checks are not native-speaker review or general proofs. The section has
no exercises or source answers, so this module checks preservation and links.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION_IDS = ("fs-id1165135203679", "fs-id1165137692068")
TABLE_ID = "eip-id1165134393730"
LIST_ID = "fs-id1165137851183"
STOP = "fs-id1165137737761"
ROW_NAMES = (
    ("Constant function", "Hàm số hằng"),
    ("Identity function", "Hàm số đồng nhất"),
    ("Absolute value function", "Hàm số giá trị tuyệt đối"),
    ("Quadratic function", "Hàm số bậc hai cơ bản"),
    ("Cubic function", "Hàm số bậc ba cơ bản"),
    ("Reciprocal function", "Hàm số lấy nghịch đảo"),
    ("Reciprocal squared function", "Hàm số lấy nghịch đảo của bình phương"),
    ("Square root function", "Hàm số căn bậc hai"),
    ("Cube root function", "Hàm số căn bậc ba"),
)


def reader_map():
    mapping = {}
    for first, last, unit, slug in (
        (1, 2, "A30-U001", "A30-U001-functions"),
        (3, 4, "A30-U002", "A30-U002-function-notation"),
        (5, 5, "A30-U003", "A30-U003-tables"),
        (6, 12, "A30-U004", "A30-U004-input-output"),
        (13, 13, "A30-U005", "A30-U005-one-to-one"),
        (14, 15, "A30-U006", "A30-U006-graph-tests"),
    ):
        for number in range(first, last + 1):
            identity = f"Example_01_01_{number:02d}"
            mapping[identity] = (unit, slug + ".vi.html")
    return mapping


class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        identity = dict(attrs).get("id")
        if identity:
            self.ids.add(identity)


def tests():
    source_tree = ET.parse(ROOT / "sources/m49301-key-summary-source.cnxml")
    source = source_tree.getroot()
    by_id = {node.get("id"): node for node in source.iter() if node.get("id")}
    markdown = (ROOT / "translation/A30-U008-key-summary.vi.md").read_text(encoding="utf-8")
    count = 0

    def check(condition, message):
        nonlocal count
        assert condition, message
        count += 1

    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    check(set(by_id) == {*SECTION_IDS, TABLE_ID, LIST_ID}, "four source IDs")
    for identity in by_id:
        check("{#" + identity + "}" in markdown, f"explicit source anchor {identity}")
    check(len(list(source.iter(CN + "section"))) == 2, "two complete summary sections")
    check(len(list(source.iter(CN + "table"))) == 1, "one source table")
    check(len(list(source.iter(CN + "item"))) == 11, "eleven concept items")
    check(not list(source.iter(CN + "exercise")), "no source exercises")
    check(not list(source.iter(CN + "image")), "no source images")
    maths = list(source.iter(M + "math"))
    check(len(maths) == 11, "eleven original MathML occurrences")
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        candidates = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(candidates), f"valid math index {identity}:{index}")
        inserted.append(candidates[int(index)])
    check(Counter(map(id, inserted)) == Counter(map(id, maths)), "each source math exactly once")
    rows = by_id[TABLE_ID].findall(f"{CN}tgroup/{CN}tbody/{CN}row")
    check(len(rows) == 9, "nine source formula rows")
    for number, (row, names) in enumerate(zip(rows, ROW_NAMES)):
        first_cell = row.find(CN + "entry")
        check("".join(first_cell.itertext()).strip() == names[0], f"source row {number + 1}")
        check(f"<tr><td>{names[1]}</td>" in markdown, f"Vietnamese row {number + 1}")
    check(markdown.count('<th scope="col">') == 2, "two accessible column headings")
    check([node.text for node in by_id[TABLE_ID].iter(M + "mn")] == ["2", "3", "1", "1", "2", "3"],
          "source formula number tokens")
    for tag, expected in (("mfrac", 2), ("msqrt", 1), ("mroot", 1), ("msup", 3)):
        check(len(list(by_id[TABLE_ID].iter(M + tag))) == expected, f"formula structure {tag}")

    mapping = reader_map()
    expected_targets = list(mapping)
    source_targets = [link.get("target-id") for link in source.iter(CN + "link")]
    check(source_targets == expected_targets, "all fifteen source references in order")
    translated_links = re.findall(r"\]\((A30-U\d{3}-[^)]+\.vi\.html)#(Example_01_01_\d{2})\)", markdown)
    check(translated_links == [(filename, identity) for identity, (unit, filename) in mapping.items()],
          "all fifteen exact reader-relative links in order")
    registry = json.loads((ROOT / "units.json").read_text(encoding="utf-8"))
    parsed_readers = {}
    for identity, (unit, filename) in mapping.items():
        check(registry[unit]["slug"] + ".vi.html" == filename, f"current reader filename {unit}")
        path = ROOT / "review" / filename
        check(path.is_file(), f"reader exists: {filename}")
        if filename not in parsed_readers:
            reader = Ids()
            reader.feed(path.read_text(encoding="utf-8"))
            parsed_readers[filename] = reader.ids
        check(identity in parsed_readers[filename], f"target anchor exists: {filename}#{identity}")

    original_path = ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"
    if original_path.exists():
        original = ET.parse(original_path)
        originals = [original.find(f".//{CN}section[@id='{identity}']") for identity in SECTION_IDS]
        for identity, original_section in zip(SECTION_IDS, originals):
            check(ET.tostring(by_id[identity]).rstrip() == ET.tostring(original_section).rstrip(),
                  f"unaltered source excerpt {identity}")
        parent = next(node for node in original.iter() if originals[0] in list(node))
        siblings = list(parent)
        offset = siblings.index(originals[0])
        check(siblings[offset + 1] is originals[1], "summary sections are contiguous")
        check(siblings[offset + 2].get("id") == STOP, "stop before Section Exercises")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure/cross-reader assertions")
