"""Assemble the complete source-ordered Marathi A20:m81374 XML draft.

Default/check mode reads only repository-relative raw module witnesses, frozen
MR-BRIDGE-012--022 inputs, fragments, notices and canonical assets.  The
explicit --capture-source bootstrap reads only the two exact named ZIP members.
No network, browser, HTML/PDF, general extraction or shared-ledger mutation.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
UNIT = "A20-m81374"
MODULE = "m81374"
UUID = "4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SOURCE_DIR = "provenance/A20-m81374-assembly"
OUTPUT = "translations/A20-m81374.xml"
RECEIPT = "qa/A20-m81374-assembly-receipt.json"
UNITS = tuple(f"MR-BRIDGE-{number:03d}" for number in range(12, 23))

SOURCE_PINS = {
    "en": (
        "A20-canonical.zip",
        "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml",
        "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a",
        247327,
        "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
    ),
    "id": (
        "A20-v0.3.0-source.zip",
        "source/modules/m81374/index.cnxml",
        "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e",
        247303,
        "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
    ),
}

# Stable, independently reviewed MR012--022 target/config/lock bytes.  A unit
# edit requires a deliberate new integration, never silent absorption here.
UNIT_PINS = {
    "MR-BRIDGE-012": ((33878, "1883fddbb24d1d3518e6d34ebdec38c608ebcee78872af069dc7030f6920402b"), (3486, "cb9c08d87b32ca61cfc2a59b3638700197666c3375a91a343e51c32516263454"), (56317, "c85ef3350201e4364853f25718a6d18f7029c248047b92ddd03252f7386029b6")),
    "MR-BRIDGE-013": ((64372, "aff28c7c2fe88ea2f638c6a19c5555a043e43bba6f7d67285d46ab20cee6ae06"), (9762, "5044fd0797fe0412589b6ad53529770cea8dabc2956c90d975813789962f50b3"), (163251, "d942abeb3bd8fd0c08439a6d0f4b9622d35e0b4fdd8bc4415b235b900e97629f")),
    "MR-BRIDGE-014": ((41927, "bcbf366d702bf38c7fd434da5ac8bb56183885962ae7eec2b7c62672c4a69885"), (4393, "ec8e6ed0bae4807c2aa36537456f6f07d4ec76259827c803b7b76c84b63cf38b"), (49987, "3577b5536628c18d6485937f1b53be0b513162f0e46f79a719aeadbe05f7b92e")),
    "MR-BRIDGE-015": ((93034, "ec72c545cc5d3e34446d2875c48778c69cd51bf631598842f35f1f740bc8865e"), (16472, "dd6b3e480731effcf5c285adbc019bf26941e2ed7aa86a974244c2f289a9f9e0"), (236772, "96b15c6573e559e6ed0735aa37ca40da93c565f8fa23d49ead836616a373fc06")),
    "MR-BRIDGE-016": ((36416, "cb4f1a89aa7d0762f003898aaef5315bccad05d5b61dc94e0011a4232f229025"), (4941, "85cdd3e51d3378fe82b99cf130f2f7925c948c68b52c1ba4cd65bd37de1e7b5c"), (121267, "689ddf28c14356985a14975dae9047669694643e7dcf8a95ff49927d93e4c99a")),
    "MR-BRIDGE-017": ((43757, "f868cd613b00687a133ad6ede745749a3d78d0a7ac1e4fb4d700a9bf6b38cbf1"), (4955, "48f84cca5607f9faa224a85c877b4af6e713bc2c6e0452adb39db5521a37d860"), (138123, "9b71760ec987da9622e6a55b3737b2a2da34d58e26a41e4ef0d98084f5c70c6b")),
    "MR-BRIDGE-018": ((32346, "f7b37554ff6973e523952578d742fda63eaa75962cd7a32369f266d2de2ec60a"), (4519, "b374350df5b6fd3db857ee8726a65ccbcdb7888fe32aabaa111eaf510482cd4c"), (97307, "d7d13b2352c6aa829db9c57e38059b730cff8faf0f9af21ae214ad8238fa6aad")),
    "MR-BRIDGE-019": ((35111, "6526da308eb86745274ff61b66fd162b8319211df9c9d3dcdd5b87323c3986d1"), (4340, "aecc60b2d9ae157e3adb75c2b240a846ec8dbf53d74d5ef53a862311c3570fcd"), (68689, "35dc46f4ebd7017cf5117091cdcabdefacf10cfd619d65fed23138954c9c3b6f")),
    "MR-BRIDGE-020": ((31109, "29bd937f6d0e23cd68a6c4a1061d7115cc4a5838fa50373a405e951aaf6f57c7"), (4285, "22051ef0fa149c8a4e0f432a7172d2d23159d08224beb0014f5be1c352fbbe36"), (89571, "6ce2fc3934f8c3b27c229dd0c5623b4bf37893c6ad54e9708f10c53e1c1b2382")),
    "MR-BRIDGE-021": ((49033, "d179b984c1f22e796831e9f7d001e3b40634df8cc269c6c6b2e76e0fe0fcc5c9"), (7709, "6f210e5cb2266acf23214379684efa336f32c39bb0c3e1aa4621f275826ac4a6"), (110903, "0128fa9f9e7fab0b5e9e68cfbd70d58e84495a13eb79260b2b9d1e41af8fcbc8")),
    "MR-BRIDGE-022": ((44623, "ec136afe3b909a855882c2b50dd1a34fb2ecd90aeaf15206326bbd2e9a176b66"), (6669, "17d561931c667a68ba00b9644fc9a5ef15e5ab5eb52ffbeca291c925cb7e39ea"), (100801, "a3f0e9ade78d7e967bc4a47bc29b2a06158e15aa9d600bc2d7ea4ca08553275c")),
}

EXPECTED_COUNTS = (18, 47, 12, 63, 40, 50, 35, 21, 33, 31, 30)

# Fourteen source structural wrappers have no data-source selectors.  Use one
# reviewed Marathi heading shell for each.  The repeated Chapter Review shell
# is deliberately taken only from016; its six children come from016--021.
WRAPPER_OWNERS = {
    "fs-id1167836579284": "MR-BRIDGE-012",
    "fs-id1167836522816": "MR-BRIDGE-013",
    "fs-id1167836386547": "MR-BRIDGE-014",
    "fs-id1167836310305": "MR-BRIDGE-015",
    "fs-id1167836300671": "MR-BRIDGE-015",
    "fs-id1167836602786": "MR-BRIDGE-015",
    "fs-id1167836524742": "MR-BRIDGE-016",
    "fs-id1167824674139": "MR-BRIDGE-016",
    "fs-id1167829740806": "MR-BRIDGE-017",
    "fs-id1167836526512": "MR-BRIDGE-018",
    "fs-id1167836570304": "MR-BRIDGE-019",
    "fs-id1167826172554": "MR-BRIDGE-020",
    "fs-id1167836699953": "MR-BRIDGE-021",
    "fs-id1167836628671": "MR-BRIDGE-022",
}

# Closed audit of all original-role nodes outside selected subtrees, headers,
# footers and other original-role nodes.  Every entry is retained exactly once.
NOTE_PLAN = {
    12: (("after", "fs-idm263727344"), ("after", "fs-id1167833386905")),
    13: (("after", "fs-id1167836692114"), ("after", "fs-id1167826171267")),
    14: (("after", "fs-id1167825884739"), ("after", "fs-id1167836515910")),
    15: (("before", "fs-id1167836300671"), ("after", "fs-id1167833181234"),
         ("after", "fs-id1167836356048"), ("after", "fs-id1167836356048"),
         ("after", "fs-id1167836579171")),
    16: (("before", "fs-id1167836689070"),),
    17: (("before", "fs-id1167833047231"), ("after", "fs-id1167836540143"),
         ("after", "fs-id1167836558141"), ("after", "fs-id1167833019834"),
         ("after", "fs-id1167836527756")),
    18: (("before", "fs-id1167836613250"), ("after", "fs-id1167829744040"),
         ("after", "fs-id1167833086732")),
    19: (("before", "fs-id1167832951212"), ("after", "fs-id1167824734423")),
    20: (("before", "fs-id1167836486019"), ("after", "fs-id1167824736070")),
    21: (("before", "fs-id1167836597214"),),
    22: (("before", "fs-id1167833142400"),),
}

MISSING_ANSWER_TEXT = {
    "स्रोतात या प्रश्नाचे उत्तर दिलेले नाही. हा प्रश्न स्वतः सोडवण्यासाठी जतन केला आहे.",
    "स्रोतात या लेखनप्रश्नाचे उत्तर दिलेले नाही. तुमचे स्पष्टीकरण स्वतः लिहा.",
    "स्रोतात या प्रश्नाचे उत्तर दिलेले नाही. स्वतः सोडवा.",
}

TABLE_ADAPTATIONS = {
    "fs-id1167836688758": {"unit": "MR-BRIDGE-013", "source_rows": 4, "source_entries": 8,
                              "checks": ("example1-slope", "example1-intercept")},
    "fs-id1167836560655": {"unit": "MR-BRIDGE-013", "source_rows": 3, "source_entries": 6,
                              "checks": ("example2-intercept",)},
}


def text(node):
    return "".join(node.itertext()).strip()


def normalized_text(node):
    return " ".join(text(node).split())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def object_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def safe_path(base, relative):
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise ValueError("unsafe repo-relative path")
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("path escapes language directory")
    result = (Path(base) / candidate).resolve()
    if not result.is_relative_to(Path(base).resolve()):
        raise ValueError("resolved path escapes language directory")
    return result


def signature(node):
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, sorted(node.attrib.items()), norm(node.text),
            [(signature(child), norm(child.tail)) for child in node])


def source_ids(node):
    return [item.get("id") for item in node.iter() if item.get("id")]


def unique_index(root):
    result = {}
    for node in root.iter():
        identity = node.get("id")
        if identity:
            if identity in result:
                raise ValueError("duplicate ID: " + identity)
            result[identity] = node
    return result


def make(tag, content=None, **attrs):
    node = ET.Element(tag, attrs)
    node.text = content
    return node


def stage_write(base, outputs):
    """Validate/stage every byte before replacing the named outputs."""
    paths = [(safe_path(base, relative), raw) for relative, raw in outputs.items()]
    with tempfile.TemporaryDirectory(prefix=".m81374-", dir=base) as temporary:
        staged = []
        for number, (destination, raw) in enumerate(paths):
            path = Path(temporary) / str(number)
            path.write_bytes(raw)
            staged.append((path, destination))
        for path, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(path, destination)


def capture_source(base=BASE):
    outputs = {}
    for locale, (archive, member, digest, size, _) in SOURCE_PINS.items():
        archive_path = Path(base).parent / "downloads/mr-Deva-IN/releases" / archive
        with zipfile.ZipFile(archive_path) as handle:
            if sum(info.filename == member for info in handle.infolist()) != 1:
                raise ValueError("ambiguous source module member")
            raw = handle.read(member)
        if sha(raw) != digest or len(raw) != size:
            raise ValueError("pinned source member drift: " + locale)
        outputs[f"{SOURCE_DIR}/{locale}-m81374.cnxml"] = raw
    stage_write(base, outputs)
    return {path: {"sha256": sha(raw), "bytes": len(raw)} for path, raw in outputs.items()}


class Assembly:
    def __init__(self, base=BASE):
        self.base = Path(base)
        self.inputs = {}
        self.roots, self.root_indices, self.configs = {}, {}, {}
        self.selected, self.selection_signatures = {}, {}
        self.assets, self.expected_math = {}, {}
        self.note_log, self.link_log = [], []
        self.header_clarification_log = []
        self.header_log, self.footer_log = [], []
        self.before, self.after = defaultdict(list), defaultdict(list)
        self.sources = {}
        self.read("tools/assemble_m81374.py")
        for locale, (_, _, digest, size, _) in SOURCE_PINS.items():
            raw = self.read(f"{SOURCE_DIR}/{locale}-m81374.cnxml")
            if sha(raw) != digest or len(raw) != size:
                raise ValueError("raw source witness drift: " + locale)
            self.sources[locale] = ET.fromstring(raw)
        self.source = self.sources["en"]
        self.source_index = unique_index(self.source)
        self.canonical_ids = list(self.source_index)
        if len(self.canonical_ids) != 1366 or self.canonical_ids != source_ids(self.sources["id"]):
            raise ValueError("complete EN/ID source identity/order drift")
        if any(sum(1 for _ in root.iter()) != 7223 for root in self.sources.values()):
            raise ValueError("complete EN/ID element census drift")
        for locale, source in self.sources.items():
            metadata = source.find(C + "metadata")
            if text(metadata.find(MD + "content-id")) != MODULE or text(metadata.find(MD + "uuid")) != UUID:
                raise ValueError("source metadata identity drift: " + locale)
        self.load_units()

    def read(self, relative):
        raw = safe_path(self.base, relative).read_bytes()
        current = {"sha256": sha(raw), "bytes": len(raw)}
        if relative in self.inputs and self.inputs[relative] != current:
            raise ValueError("input changed during assembly: " + relative)
        self.inputs[relative] = current
        return raw

    def read_json(self, relative):
        return json.loads(self.read(relative), object_pairs_hook=object_pairs)

    def read_pinned(self, relative, pin):
        raw = self.read(relative)
        if (len(raw), sha(raw)) != pin:
            raise ValueError("stable integration input drift: " + relative)
        return raw

    def load_units(self):
        counts = []
        for unit in UNITS:
            pins = UNIT_PINS[unit]
            xml_raw = self.read_pinned(f"translations/{unit}.xml", pins[0])
            root = ET.fromstring(xml_raw)
            if root.get("lang") != "mr-Deva-IN":
                raise ValueError("translation locale mismatch: " + unit)
            self.roots[unit] = root
            self.root_indices[unit] = unique_index(root)
            config_raw = self.read_pinned(f"units/{unit}.json", pins[1])
            config = json.loads(config_raw, object_pairs_hook=object_pairs)
            self.configs[unit] = config
            lock_raw = self.read_pinned(f"provenance/{unit}.lock.json", pins[2])
            lock = json.loads(lock_raw, object_pairs_hook=object_pairs)
            if lock.get("unit") != unit or lock.get("locale") != "mr-Deva-IN":
                raise ValueError("unit lock identity mismatch: " + unit)
            witnesses = {record["path"]: record["sha256"] for record in lock["witnesses"]}
            if len(witnesses) != len(lock["witnesses"]):
                raise ValueError("duplicate lock witness: " + unit)
            for path, digest in witnesses.items():
                if sha(self.read(path)) != digest:
                    raise ValueError("frozen witness drift: " + path)
            locked = {record["target_id"]: record for record in lock["source_selections"]}
            if len(locked) != len(lock["source_selections"]):
                raise ValueError("duplicate locked selector: " + unit)
            current = 0
            for node in root.iter():
                locator = node.get("data-source", "")
                if not locator.startswith("A20:m81374#"):
                    continue
                identity = locator.split("#", 1)[1]
                if identity not in self.source_index or node.get("id") != identity or identity in self.selected:
                    raise ValueError("unknown, duplicate or mismatched selection: " + identity)
                if identity not in locked or locked[identity]["locator"] != locator:
                    raise ValueError("selection not frozen: " + identity)
                sources = locked[identity]["sources"]
                if [record["locale"] for record in sources] != ["en", "id"]:
                    raise ValueError("selection locale provenance drift: " + identity)
                for frozen in sources:
                    locale = frozen["locale"]
                    pin = SOURCE_PINS[locale]
                    if (frozen["module_sha256"] != pin[2] or frozen["member"] != pin[1]
                            or frozen["archive_sha256"] != pin[4]):
                        raise ValueError("selection source pin drift: " + identity)
                    fragment = self.read(frozen["fragment_path"])
                    if sha(fragment) != frozen["fragment_sha256"]:
                        raise ValueError("fragment hash drift: " + frozen["fragment_path"])
                    original = self.source_index[identity] if locale == "en" else unique_index(self.sources[locale])[identity]
                    if signature(ET.fromstring(fragment)) != signature(original):
                        raise ValueError("fragment differs from complete source: " + identity)
                self.selected[identity] = (unit, node)
                current += 1
            if set(locked) != {identity for identity, (owner, _) in self.selected.items() if owner == unit}:
                raise ValueError("lock/target selector inventory drift: " + unit)
            counts.append(current)
            headers = root.findall("header")
            footers = root.findall("footer")
            if len(headers) != 1 or len(footers) != 1 or footers[0].get("id") != "credits":
                raise ValueError("unit header/footer inventory drift: " + unit)
            self.header_log.append({"unit": unit, "input_xml_sha256": sha(ET.tostring(headers[0])),
                                    "disposition": "replaced by one synthesized module header; objective selectors retained separately"})
            self.footer_log.append({"unit": unit, "input_xml_sha256": sha(ET.tostring(footers[0])),
                                    "disposition": "replaced by one synthesized module footer; notices remain pinned inputs"})
        if tuple(counts) != EXPECTED_COUNTS or len(self.selected) != 380:
            raise ValueError("380-selector scope drift")
        covered = Counter(item.get("id") for identity in self.selected
                          for item in self.source_index[identity].iter() if item.get("id"))
        if any(count != 1 for count in covered.values()):
            raise ValueError("overlapping selected subtrees")
        missing = set(self.canonical_ids) - set(covered)
        if missing != set(WRAPPER_OWNERS):
            raise ValueError("unaccounted canonical source gap")
        chapter = "fs-id1167836524742"
        chapter_owners = [unit for unit in UNITS if chapter in self.root_indices[unit]]
        if chapter_owners != list(UNITS[4:10]):
            raise ValueError("repeated Chapter Review wrapper inventory drift")
        for identity, owner in WRAPPER_OWNERS.items():
            if identity not in self.root_indices[owner]:
                raise ValueError("wrapper owner lost reviewed heading: " + identity)

    def copy(self, unit, node):
        cloned = deepcopy(node)
        cloned.tail = None
        cloned.set("data-origin-unit", unit)
        for item in cloned.iter():
            identity = item.get("id")
            if identity and identity not in self.source_index:
                item.set("data-origin-id", identity)
                item.set("id", unit + "--" + identity)
            key = item.get("data-check")
            if key:
                value = text(item)
                if self.configs[unit].get("expected_math", {}).get(key) != value:
                    raise ValueError("math differs from reviewed config: " + unit + ":" + key)
                namespaced = unit + "::" + key
                if namespaced in self.expected_math:
                    raise ValueError("duplicate assembly math key: " + namespaced)
                self.expected_math[namespaced] = value
                item.set("data-origin-check", key)
                item.set("data-check", namespaced)
            if item.tag == "a":
                href = item.get("href", "")
                document = item.get("data-source-document")
                target = item.get("data-source-target-id")
                same_module = document == MODULE or (document is None and target in self.source_index)
                if same_module:
                    if target is not None and target not in self.source_index:
                        raise ValueError("unknown same-module target")
                    new_href = "#" + (target or UNIT)
                    item.set("data-prior-href", href)
                    item.set("href", new_href)
                    self.link_log.append({"unit": unit, "document": document or MODULE,
                                          "target": target, "old_href": href, "new_href": new_href})
                elif document is not None or target is not None:
                    if not href.startswith("https://"):
                        raise ValueError("outside-module source link is not HTTPS")
                elif href.startswith("#"):
                    target = href[1:]
                    if target not in self.source_index and target not in {UNIT, "credits"}:
                        item.set("href", "#" + unit + "--" + target)
            if item.tag == "img":
                route = item.get("src", "")
                if not route.startswith("asset:"):
                    raise ValueError("unreviewed image route")
                name = route[6:]
                asset = self.configs[unit].get("assets", {}).get(name)
                if not asset:
                    raise ValueError("source image has no frozen canonical asset")
                raw = self.read(asset["path"])
                if sha(raw) != asset["sha256"]:
                    raise ValueError("canonical asset drift: " + asset["path"])
                if asset["path"] in self.assets:
                    raise ValueError("canonical source image reused unexpectedly")
                item.set("data-origin-src", route)
                item.set("src", "../" + asset["path"])
                self.assets[asset["path"]] = {"sha256": sha(raw), "bytes": len(raw), "mime": asset["mime"]}
        return cloned

    def outer_notes(self, root):
        parents = {child: parent for parent in root.iter() for child in parent}
        result = []
        for node in root.iter():
            if node.get("data-kind") != "original":
                continue
            ancestors, current = [], node
            while current in parents:
                current = parents[current]
                ancestors.append(current)
            if any(ancestor.tag in {"header", "footer"} or ancestor.get("id") == "credits"
                   or ancestor.get("data-kind") == "original"
                   or ancestor.get("data-source", "").startswith("A20:m81374#")
                   for ancestor in ancestors):
                continue
            result.append(node)
        return result

    def prepare_notes(self):
        for unit in UNITS:
            number = int(unit[-3:])
            notes = self.outer_notes(self.roots[unit])
            plan = NOTE_PLAN[number]
            if len(notes) != len(plan):
                raise ValueError("unreviewed outer authored note inventory: " + unit)
            for index, (node, (placement, anchor)) in enumerate(zip(notes, plan)):
                if anchor not in self.source_index:
                    raise ValueError("outer-note anchor is not canonical: " + anchor)
                copied = self.copy(unit, node)
                marker = f"{unit}:{index}"
                copied.set("data-assembly-note", marker)
                record = {"unit": unit, "outer_note_index": index,
                          "input_xml_sha256": sha(ET.tostring(node)), "placement": placement,
                          "anchor": anchor, "treatment": "retain complete node",
                          "output_signature_sha256": sha(repr(signature(copied)).encode("utf-8"))}
                self.note_log.append(record)
                (self.before if placement == "before" else self.after)[anchor].append(copied)
        if len(self.note_log) != 26:
            raise ValueError("26-note disposition census drift")
        # One substantive graph/domain clarification lives in013's unit header.
        # It is outside the 26-node outer-note census but supplies two of the
        # audited 685 checks, so retain it explicitly after the objectives.
        for unit in UNITS:
            asides = self.roots[unit].findall("header/aside")
            expected = 1 if unit == "MR-BRIDGE-013" else 0
            if len(asides) != expected:
                raise ValueError("substantive header clarification inventory drift: " + unit)
            if expected:
                copied = self.copy(unit, asides[0])
                copied.set("data-assembly-header-note", unit + ":0")
                self.after["list-00001"].append(copied)
                self.header_clarification_log.append({
                    "unit": unit, "header_aside_index": 0,
                    "input_xml_sha256": sha(ET.tostring(asides[0])),
                    "placement": "after", "anchor": "list-00001",
                    "treatment": "retain substantive graph/domain clarification",
                })

    def wrapper_heading(self, identity):
        owner = WRAPPER_OWNERS[identity]
        wrapper = self.root_indices[owner][identity]
        headings = [child for child in wrapper if child.tag in {"h2", "h3", "h4", "h5", "h6"}]
        if len(headings) != 1:
            raise ValueError("reviewed wrapper heading inventory drift: " + identity)
        return owner, self.copy(owner, headings[0])

    def emit(self, source):
        identity = source.get("id")
        if identity in self.selected:
            unit, node = self.selected[identity]
            result = self.copy(unit, node)
            result.set("data-source-tag", source.tag.split("}")[-1])
            self.selection_signatures[identity] = signature(result)
        elif identity in WRAPPER_OWNERS:
            owner, heading = self.wrapper_heading(identity)
            result = make("section", id=identity, **{"data-kind": "source-context",
                          "data-source-tag": "section", "data-origin-unit": owner})
            if source.get("class"):
                result.set("data-source-class", source.get("class"))
            result.append(heading)
            for child in source:
                if child.tag == C + "title":
                    continue
                result.extend(self.emit(child))
        else:
            raise ValueError("unselected source content: " + str(identity) + " " + source.tag)
        return self.before[identity] + [result] + self.after[identity]

    def build(self):
        self.prepare_notes()
        root = make("article", id=UNIT, lang="mr-Deva-IN", **{
            "data-source-document": MODULE, "data-source-uuid": UUID,
            "data-status": "assembled-translation-draft", "data-reader-accepted": "false"})
        header = ET.SubElement(root, "header")
        header.append(make("p", "A20 · Intermediate Algebra 2e · m81374", **{"class": "eyebrow"}))
        header.append(make("h1", "फलनांचे आलेख"))
        header.append(make("p", "स्रोताच्या क्रमातील संपूर्ण एकत्रित अनुवाद-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, विभाग-सराव, धड्याची उजळणी, सराव चाचणी, स्रोत-उत्तरे आणि उत्तर नसलेल्या प्रश्नांच्या स्पष्ट नोंदी येथे एकत्र आहेत. दुरुस्त्या व जोडस्पष्टीकरणे स्वतंत्र लेखक-भूमिकेत राहतात. हा HTML/PDF वाचक, मानवी मान्यता, संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा पूर्ण कार्यप्रवाह नाही.", **{"data-kind": "original"}))
        metadata = ET.SubElement(header, "dl", {"class": "source-metadata", "data-kind": "original"})
        for key, value in (("मूळ इंग्रजी शीर्षक", "Graphs of Functions"),
                           ("इंडोनेशियन शीर्षक", "Grafik Fungsi"),
                           ("स्रोत दस्तऐवज", MODULE), ("स्रोत UUID", UUID)):
            metadata.append(make("dt", key)); metadata.append(make("dd", value))
        header.append(make("p", "घटक 12–22 मधील स्थिर, स्वतंत्रपणे स्रोत/गणित तपासलेले मसुदे वापरले आहेत. घटकांतील स्थानिक प्रश्न व उदाहरण क्रमांक मूळ पुस्तकाचे जागतिक क्रमांक मानू नयेत; 1,366 मूळ ओळखचिन्हे, स्रोतक्रम आणि उतरंड हे निश्चित संदर्भ आहेत. वारंवार आलेला धडा-उजळणी आवरण एकदाच ठेवून त्याचे सहा विषयगट मूळ क्रमाने जोडले आहेत.", **{"data-kind": "original"}))
        objectives = ET.SubElement(root, "section", {"id": "assembly-objectives", "data-kind": "source-context"})
        objectives.append(make("h2", "या विभागाची उद्दिष्टे", **{"data-kind": "original"}))
        abstract = self.source.find(C + "metadata").find(MD + "abstract")
        for child in abstract:
            objectives.extend(self.emit(child))
        content = ET.SubElement(root, "section", {"id": "assembly-content", "data-kind": "source-context"})
        for child in self.source.find(C + "content"):
            content.extend(self.emit(child))
        footer = ET.SubElement(root, "footer", {"id": "credits", "data-kind": "original"})
        footer.append(make("h2", "स्रोत, श्रेय आणि मर्यादा"))
        footer.append(make("p", "OpenStax, Intermediate Algebra 2e: Lynn Marecek आणि Andrea Honeycutt Mathis; प्रकाशक OpenStax, Rice University. पिन केलेला इंग्रजी m81374 स्रोत आणि इंडोनेशियन v0.3.0-wip समांतर आवृत्ती त्यांच्या मूळ नोंदींसह वापरली आहे. अनुवाद व एकत्रीकरण: वापरकर्त्याच्या सूचनेवरील Codex-सहाय्यित मराठी कार्यप्रवाह."))
        license_note = make("p", "निवडक स्रोत व मराठी अनुकूलन: ")
        license_link = make("a", "CC BY-NC-SA 4.0", href="https://creativecommons.org/licenses/by-nc-sa/4.0/")
        license_link.tail = "; स्वतंत्र घटक/तृतीय-पक्ष सूचना कायम लागू आहेत. पिन केलेले परवाना व श्रेय-साक्षी या एकत्रीकरणाच्या पावतीतील पुनर्बांधणी इनपुटमध्ये आहेत."
        license_note.append(license_link); footer.append(license_note)
        footer.append(make("p", "149 मूळ इंग्रजी स्रोत-आकृत्या त्यांच्या स्थिर घटक-assets संचिकांतून अचूक हॅशसह जोडल्या आहेत. दोन स्रोत-गणना तक्ते आधीच्या तपासलेल्या मसुद्यातील रेषीय परिच्छेद-अनुकूलन म्हणून राहतात; सात स्रोत-रांगा व चौदा नोंदींची स्वतंत्र पावती आहे. दुरुस्त पर्यायी वर्णने, संदर्भ-अटी, पुरवलेली स्रोत-उत्तरे आणि स्पष्ट उत्तर-उणीव या भूमिका बदललेल्या नाहीत."))
        footer.append(make("p", "हा स्रोत-संरचना मसुदा आहे. कोणतेही HTML/PDF तयार किंवा पाहिलेले नाही; वाचक-मांडणी, प्रवेशयोग्यता, मातृभाषिक/मानवी गणित-शिक्षक मान्यता, संपूर्ण A20 पुस्तक किंवा संपूर्ण पाच-पुस्तकांचे काम पूर्ण झाल्याचा दावा नाही. पुढील m81375 आणि उर्वरित संपूर्ण नियुक्तीचे उत्पादन स्वतंत्रपणे सुरू राहते."))
        self.validate(root)
        ET.indent(root, space="  ")
        raw = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
        receipt = self.receipt(root, raw)
        for relative, record in self.inputs.items():
            current = safe_path(self.base, relative).read_bytes()
            if len(current) != record["bytes"] or sha(current) != record["sha256"]:
                raise ValueError("input changed before output: " + relative)
        return raw, json_bytes(receipt)

    @staticmethod
    def omission_nodes(node):
        result = []
        for item in node.iter():
            classes = item.get("class", "").split()
            if "source-answer-missing" in classes or (item.get("data-kind") == "original"
                    and normalized_text(item) in MISSING_ANSWER_TEXT):
                result.append(item)
        return result

    def validate(self, root):
        target = unique_index(root)
        actual = [identity for identity in target if identity in self.source_index]
        if actual != self.canonical_ids:
            raise ValueError("canonical 1366-ID order/preservation failed")
        for identity, original in self.source_index.items():
            descendants = [item.get("id") for item in target[identity].iter()
                           if item.get("id") in self.source_index]
            if descendants != source_ids(original):
                raise ValueError("canonical ancestry mismatch: " + identity)
        selectors = [item.get("id") for item in root.iter()
                     if item.get("data-source", "").startswith("A20:m81374#")]
        expected_selectors = [identity for identity in self.canonical_ids if identity in self.selected]
        if selectors != expected_selectors or len(selectors) != 380:
            raise ValueError("selector order/preservation failed")
        for identity, expected in self.selection_signatures.items():
            if signature(target[identity]) != expected:
                raise ValueError("selected translated content changed during assembly: " + identity)
        if set(item.get("data-assembly-note") for item in root.iter() if item.get("data-assembly-note")) != {
                f"{record['unit']}:{record['outer_note_index']}" for record in self.note_log}:
            raise ValueError("outer authored note preservation failed")
        exercises = list(self.source.iter(C + "exercise"))
        solutions = list(self.source.iter(C + "solution"))
        unsupplied = [exercise for exercise in exercises if exercise.find(C + "solution") is None]
        if (len(exercises), len(solutions), len(unsupplied)) != (255, 141, 114):
            raise ValueError("source answer inventory drift")
        omission_count = 0
        for exercise in exercises:
            current = target[exercise.get("id")]
            problem = exercise.find(C + "problem")
            if problem.get("id") not in source_ids(current):
                raise ValueError("exercise lost original problem")
            supplied = exercise.find(C + "solution")
            omissions = self.omission_nodes(current)
            if supplied is None:
                if len(omissions) != 1:
                    raise ValueError("source answer omission not explicit exactly once: " + exercise.get("id"))
                omission_count += 1
            else:
                if supplied.get("id") not in source_ids(current) or omissions:
                    raise ValueError("supplied answer lost or mislabeled: " + exercise.get("id"))
                hrefs = [link.get("href") for link in current.iter("a")]
                if "#" + supplied.get("id") not in hrefs or "#" + problem.get("id") not in hrefs:
                    raise ValueError("supplied answer navigation lost: " + exercise.get("id"))
        if omission_count != 114 or any(identity.startswith("mr-answer-") for identity in target):
            raise ValueError("answer-role inventory changed")
        checks = {}
        for item in root.iter():
            key = item.get("data-check")
            if key:
                if key in checks or "::" not in key:
                    raise ValueError("duplicate or unnamespaced math key")
                checks[key] = text(item)
            if item.tag == "a":
                href = item.get("href", "")
                if href.startswith("#"):
                    if href[1:] not in target or not text(item):
                        raise ValueError("unresolved local link: " + href)
                elif not href.startswith("https://"):
                    raise ValueError("unreviewed link route: " + href)
        if checks != self.expected_math or len(checks) != 685:
            missing = sorted(set(self.expected_math) - set(checks))
            extra = sorted(set(checks) - set(self.expected_math))
            changed = sorted(key for key in set(checks) & set(self.expected_math)
                             if checks[key] != self.expected_math[key])
            raise ValueError(f"685 checked mathematical strings changed: output={len(checks)} "
                             f"expected={len(self.expected_math)} missing={missing[:3]} "
                             f"extra={extra[:3]} changed={changed[:3]}")
        if len(list(self.source.iter(M + "math"))) != 481:
            raise ValueError("source MathML census drift")
        images = list(root.iter("img"))
        if len(images) != 149 or len(self.assets) != 149 or sum(record["bytes"] for record in self.assets.values()) != 9908130:
            raise ValueError("canonical image census drift")
        source_names = [Path(item.get("src")).name for item in self.source.iter(C + "image")]
        target_names = [item.get("data-origin-src", "")[6:] for item in images]
        if source_names != target_names or len(set(target_names)) != 149:
            raise ValueError("canonical image order/identity drift")
        for item in images:
            route = item.get("src", "")
            if not route.startswith("../assets/") or route[3:] not in self.assets or "\\" in route or ":" in route:
                raise ValueError("unsafe or unpinned image route")
        source_link_counter = Counter((item.get("document", MODULE), item.get("target-id"))
                                      for item in self.source.iter(C + "link") if not item.get("url"))
        target_links = [item for item in root.iter("a")
                        if item.get("data-source-document") is not None or item.get("data-source-target-id") is not None]
        target_link_counter = Counter((item.get("data-source-document", MODULE), item.get("data-source-target-id"))
                                      for item in target_links)
        if target_link_counter != source_link_counter:
            raise ValueError("source link identity/multiplicity drift")
        same_module = [item for item in target_links if item.get("data-source-document", MODULE) == MODULE]
        outside = [item for item in target_links if item.get("data-source-document", MODULE) != MODULE]
        if len(same_module) != 6 or any(not item.get("href", "").startswith("#") for item in same_module):
            raise ValueError("same-module links were not deliberately localized")
        if len(outside) != 8 or any(not item.get("href", "").startswith("https://") for item in outside):
            raise ValueError("outside-module links were falsely localized")
        if len(self.link_log) != 6 or sum(item.get("href") == "https://openstax.org/l/37domainrange"
                                          for item in root.iter("a")) != 1:
            raise ValueError("localized/optional source link policy drift")
        rating = [item for item in root.iter("table")
                  if item.get("data-origin-id") == "MR-BRIDGE-015-self-rating"]
        if len(rating) != 1:
            raise ValueError("self-rating adaptation missing")
        blanks = list(rating[0].iter("td"))
        if len(blanks) != 9 or any(item.attrib or len(item) or normalized_text(item) for item in blanks):
            raise ValueError("nine self-rating cells must remain blank")
        table_rows = table_entries = 0
        for identity, policy in TABLE_ADAPTATIONS.items():
            source_table = self.source_index[identity]
            rows = len(list(source_table.iter(C + "row")))
            entries = len(list(source_table.iter(C + "entry")))
            if (rows, entries) != (policy["source_rows"], policy["source_entries"]):
                raise ValueError("source linear table census drift")
            if target[identity].tag != "div" or list(target[identity].iter("table")):
                raise ValueError("reviewed linear table adaptation changed")
            for key in policy["checks"]:
                if policy["unit"] + "::" + key not in checks:
                    raise ValueError("linear table adaptation lost checked value")
            table_rows += rows; table_entries += entries
        if (table_rows, table_entries) != (7, 14):
            raise ValueError("linear table adaptation total drift")
        if len(root.findall("header")) != 1 or len(root.findall("footer")) != 1:
            raise ValueError("module header/footer synthesis drift")
        if normalized_text(root.find("header/h1")) != "फलनांचे आलेख" or root.find("footer").get("id") != "credits":
            raise ValueError("module title/footer identity drift")

    def receipt(self, root, raw):
        wrappers = {}
        for identity, owner in WRAPPER_OWNERS.items():
            source_title = self.source_index[identity].find(C + "title")
            heading = next(child for child in unique_index(root)[identity]
                           if child.tag in {"h2", "h3", "h4", "h5", "h6"})
            wrappers[identity] = {"owner": owner, "source_title": normalized_text(source_title),
                                  "marathi_heading": normalized_text(heading)}
        table_policy = []
        for identity, policy in TABLE_ADAPTATIONS.items():
            table_policy.append({"source_table_id": identity, "unit": policy["unit"],
                                 "source_rows": policy["source_rows"],
                                 "source_entries": policy["source_entries"],
                                 "treatment": "reviewed linear paragraph adaptation retained; no source row/entry treated as a new question"})
        return {
            "schema": 1, "module": "A20:m81374", "status": "assembled_translation_draft",
            "reader_accepted": False, "pdf_generated": False, "full_workflow_complete": False,
            "output": {"path": OUTPUT, "sha256": sha(raw), "bytes": len(raw)},
            "source_metadata": {"content_id": MODULE, "uuid": UUID, "en_title": "Graphs of Functions",
                                "id_title": "Grafik Fungsi", "mr_title": "फलनांचे आलेख"},
            "source_members": {locale: {"path": f"{SOURCE_DIR}/{locale}-m81374.cnxml",
                                         "sha256": pin[2], "bytes": pin[3],
                                         "original_archive": "downloads/mr-Deva-IN/releases/" + pin[0],
                                         "original_member": pin[1], "recorded_archive_sha256": pin[4],
                                         "archive_required_for_default_rebuild": False}
                               for locale, pin in SOURCE_PINS.items()},
            "counts": {"source_elements_per_locale": 7223, "canonical_ids": 1366,
                       "unique_ordered_nonnested_selectors": 380, "rebuilt_source_wrappers": 14,
                       "outer_authored_nodes_retained": 26, "source_exercises": 255,
                       "source_supplied_answers": 141, "explicit_source_answer_omissions": 114,
                       "source_mathml": 481, "namespaced_target_checks": 685,
                       "canonical_assets": 149, "canonical_asset_bytes": 9908130,
                       "blank_self_rating_cells": 9, "adapted_linear_source_tables": 2,
                       "adapted_linear_source_rows": 7, "adapted_linear_source_entries": 14,
                       "localized_same_module_source_links": 6,
                       "external_outside_module_source_links": 8, "optional_external_resources": 1},
            "selection_order": [{"locator": "A20:m81374#" + identity,
                                 "unit": self.selected[identity][0]}
                                for identity in self.canonical_ids if identity in self.selected],
            "canonical_id_order": self.canonical_ids,
            "wrapper_policy": {"wrappers": wrappers,
                               "chapter_review": {"id": "fs-id1167836524742",
                                                  "shell_owner": "MR-BRIDGE-016",
                                                  "child_owners_in_source_order": list(UNITS[4:10]),
                                                  "treatment": "collapse six repeated unit shells to one source wrapper and retain all six topic children"}},
            "outer_authored_node_dispositions": self.note_log,
            "table_adaptations": table_policy,
            "link_policy": {"same_module": "local fragment routes, preserving prior href",
                            "outside_module": "HTTPS routes retained", "localized_links": self.link_log},
            "header_policy": {"synthesized_module_headers": 1, "unit_header_dispositions": self.header_log,
                              "objective_selectors_retained": ["para-00001", "list-00001"],
                              "substantive_header_clarifications_retained": self.header_clarification_log},
            "footer_policy": {"synthesized_module_footers": 1, "unit_footer_dispositions": self.footer_log,
                              "notice_policy": "frozen notices remain reconstruction inputs; no supply/license re-audit"},
            "role_policy": "Stable selected subtrees and all 26 audited outer nodes retain translation/original/adaptation, correction, attribution and answer-omission roles; transport only namespaces authored IDs/checks and localizes safe routes.",
            "assets": self.assets, "expected_math": self.expected_math,
            "inputs": dict(sorted(self.inputs.items())),
            "limits": ["No browser, HTML or PDF was used, generated or inspected.",
                       "This assembly is not a reader-format, accessibility, semantic/pixel re-review, human/native-speaker or mathematics-teacher approval.",
                       "It completes the bounded m81374 source representation only; it is not a complete A20 book or five-book assignment.",
                       "Default rebuild reads no archive, network resource or absolute donor path.",
                       "Several output replacements are staged first but are not an atomic multi-file transaction."],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="recompute and compare without writing")
    mode.add_argument("--capture-source", action="store_true", help="bootstrap two exact raw module members only")
    args = parser.parse_args()
    if args.capture_source:
        print(json.dumps(capture_source(), indent=2))
        return
    raw, receipt = Assembly().build()
    outputs = {OUTPUT: raw, RECEIPT: receipt}
    if args.check:
        for path, expected in outputs.items():
            if safe_path(BASE, path).read_bytes() != expected:
                raise SystemExit("STALE assembly artifact: " + path)
        print("PASS: exact m81374 XML/receipt rebuild;1366 IDs,380 selectors,255 exercises,149 assets")
    else:
        stage_write(BASE, outputs)
        print("WROTE assembled m81374 translation draft (not an accepted reader): " + sha(raw))


if __name__ == "__main__":
    main()
