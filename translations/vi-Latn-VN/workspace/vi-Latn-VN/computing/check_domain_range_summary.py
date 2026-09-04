"""Read-only U023 source, scope, wording-guard and navigation checks.

There are no new examples, exercises, answers or mathematical formulas here.
These are structural assertions, not mathematical proofs or native review.
Default uses the committed excerpt, draft and five target drafts; a target
may await registration. --originals requires both pinned local originals.
--readers strictly requires all five registered, built readers and anchors.
"""
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165134077347"
LIST = "fs-id1165137591772"
EXCERPT_SHA = "1c6c15012530fae0a2c196dc1569a6a2b84fd08b5c23fba4f29d69dd54b96b78"
ITEM_REFERENCES = ((), (1,), (2, 3, 4), (5,), (6, 7), (8, 9, 10), (11, 12), (13,))


def reader_map():
    mapping = {}
    for first, last, unit, slug in (
        (1, 4, "A30-U018", "A30-U018-domain-equations"),
        (5, 5, "A30-U019", "A30-U019-set-notation"),
        (6, 7, "A30-U020", "A30-U020-domain-range-graphs"),
        (8, 10, "A30-U021", "A30-U021-toolkit-domains-ranges"),
        (11, 13, "A30-U022", "A30-U022-piecewise-functions"),
    ):
        for number in range(first, last + 1):
            mapping[f"Example_01_02_{number:02d}"] = (unit, slug)
    return mapping


class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = Counter()

    def handle_starttag(self, tag, attrs):
        identity = dict(attrs).get("id")
        if identity:
            self.ids[identity] += 1


def tests(originals=False, readers=False, details=False):
    counts = Counter()

    def check(condition, message, kind="source_structure_navigation"):
        assert condition, message
        counts[kind] += 1

    data = (ROOT / "sources/m49304-domain-range-summary-source.cnxml").read_bytes()
    source = ET.fromstring(data)
    md = (ROOT / "translation/A30-U023-domain-range-summary.vi.md").read_text("utf-8")
    anchors = re.findall(r"\{#([^}]+)\}", md)
    source_ids = [n.get("id") for n in source.iter() if n.get("id")]
    check(sha256(data).hexdigest() == EXCERPT_SHA, "exact reviewed source excerpt")
    check(md == unicodedata.normalize("NFC", md), "NFC Vietnamese")
    check(source_ids == [SECTION, LIST], "two module-local IDs in original order")
    check(len(anchors) == len(set(anchors)), "all explicit anchors unique")
    for identity in source_ids:
        check(anchors.count(identity) == 1, f"source anchor once: m49304/{identity}")
    for name, expected in (("section", 1), ("title", 1), ("list", 1), ("item", 8),
                           ("link", 13), ("example", 0), ("exercise", 0),
                           ("solution", 0), ("image", 0), ("table", 0)):
        check(len(list(source.iter(CN + name))) == expected, f"source {name} count")
    check(not list(source.iter(M + "math")), "zero source MathML")
    check("{{math:" not in md, "no invented source-math placeholders")
    check(not re.findall(r"!\[", md), "no introduced images")
    check("fs-id1165135176628" not in source_ids + anchors, "outer exercise heading excluded")
    section = source.find(f"{CN}content/{CN}section")
    check(section.get("class") == "key-concepts", "complete Key Concepts category")
    items = section.find(CN + "list")
    mapping = reader_map()
    check([link.get("target-id") for link in source.iter(CN + "link")] == list(mapping),
          "all thirteen source references in order")
    for number, (item, numbers) in enumerate(zip(items, ITEM_REFERENCES), 1):
        check([n.get("target-id") for n in item.iter(CN + "link")] == [
            f"Example_01_02_{value:02d}" for value in numbers],
            f"source item {number} retains its own reference group")
    translated_list = re.search(r"::: \{#" + LIST + r"\}\s*\n(.*?)\n:::", md, re.S)
    check(translated_list is not None, "source list is separately anchored")
    check(re.findall(r"^(\d+)\. ", translated_list.group(1), re.M) == list("12345678"),
          "eight translated items without reordering")
    links = re.findall(r"\[Ví dụ (\d+)\]\((A30-U\d{3}-[^)#]+\.vi\.html)#([^)]*)\)", md)
    check(links == [(str(number), slug + ".vi.html", identity)
                    for number, (identity, (_, slug)) in enumerate(mapping.items(), 1)],
          "all thirteen exact source-example reader links and labels")
    check(len(re.findall(r"\]\(A30-", md)) == 13, "no undeclared additional cross-reader links")
    plain = " ".join(md.split())
    for phrase in (
        "tập xác định thực lớn nhất của công thức",
        "Nếu đề bài đã chỉ định tập xác định, hoặc bối cảnh đặt ra giới hạn",
        "không tự mở rộng tập xác định",
        "đầu vào và đầu ra là số thực",
        "ký hiệu tập hợp theo điều kiện và ký hiệu khoảng",
        "những đầu ra **thực sự nhận được**",
        "đúng một giá trị đầu ra",
        "mọi đầu vào thuộc phần giao",
    ):
        check(phrase in plain, f"reviewed terminology/scope guard: {phrase}")
    check(md.count("*Làm rõ bổ sung") == 3, "three clearly separated clarification blocks")
    check("không phải ví dụ hay bài tập mới" in plain, "linked examples are not new coverage")
    registry = json.loads((ROOT / "units.json").read_text("utf-8"))
    for identity, (unit, slug) in mapping.items():
        target = ROOT / "translation" / (slug + ".vi.md")
        check(target.is_file(), f"target draft exists: {slug}")
        check(target.read_text("utf-8").count("{#" + identity + "}") == 1,
              f"exact target draft anchor once: m49304/{identity}")
        check(unit not in registry or registry[unit]["slug"] == slug,
              f"registered slug, when present, agrees: {unit}")

    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_domain_range_summary import ORIGINALS, extract
        for relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest, "pinned original", "originals")
            reproduced = extract(path)  # Includes exact previous/next sibling guards.
            original = ET.fromstring(reproduced)
            check([n.get("id") for n in original.iter() if n.get("id")] == source_ids,
                  "EN/ID module-qualified source identities", "originals")
            check([n.get("target-id") for n in original.iter(CN + "link")] == list(mapping),
                  "EN/ID identical reference order", "originals")
            check(not list(original.iter(M + "math")), "EN/ID zero MathML", "originals")
            if "upstream-openstax" in relative:
                check(reproduced.encode("utf-8") == data, "unaltered full EN section", "originals")

    if readers:
        parsed = {}
        for identity, (unit, slug) in mapping.items():
            check(unit in registry and registry[unit]["slug"] == slug,
                  "all reader targets registered", "readers")
            path = ROOT / "review" / (slug + ".vi.html")
            check(path.is_file(), "built reader exists", "readers")
            if slug not in parsed:
                parsed[slug] = Ids()
                parsed[slug].feed(path.read_text("utf-8"))
            check(parsed[slug].ids[identity] == 1, "unique built target anchor", "readers")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv,
                   readers="--readers" in sys.argv, details=True)
    print(f"PASS: {sum(result.values())} structural assertions; {result}; no mathematical proofs")
