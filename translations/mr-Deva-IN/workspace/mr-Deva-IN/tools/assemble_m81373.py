"""Assemble a source-ordered Marathi m81373 XML draft; never build a reader.

Default/check mode reads only small repo-relative witnesses, unit XML/configs,
frozen fragments/notices and existing canonical assets. --capture-source is a
one-time, explicit bootstrap of two exact module members from existing ZIPs.
No network, browser, HTML/PDF, corpus extraction, or shared-file mutation.
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
UNIT = "A20-m81373"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
UUID = "59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20"
SOURCE_DIR = "provenance/A20-m81373-assembly"
OUTPUT = "translations/A20-m81373.xml"
RECEIPT = "qa/A20-m81373-assembly-receipt.json"
UNITS = tuple(f"MR-BRIDGE-{n:03d}" for n in range(2, 12))
REPLACED = ("fs-id1167836692527", "fs-id1167836521479", "fs-id1167829859398", "fs-id1167833175472")
LEGACY_SHA = "367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9"
SOURCE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c", 151578,
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee", 143952,
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
CONTEXTS = {
    "fs-id1167829789538": ("MR-BRIDGE-008", "संबंधाचा प्रांत आणि मूल्यसंच शोधा"),
    "fs-id1167836610583": ("MR-BRIDGE-009", "संबंध फलन आहे का ते ठरवा"),
    "fs-id1167824731607": ("MR-BRIDGE-010", "फलनाचे मूल्य काढा"),
    "fs-id1167829756260": ("MR-BRIDGE-007", "लेखी सराव"),
}
WRAPPERS = {"fs-id1167826170977", "fs-id1167826189010"}
EXPECTED_COUNTS = (4, 1, 16, 16, 31, 9, 21, 14, 18, 4)
# Explicit dispositions of outer authored content, excluding excerpt headers.
# Each entry is (placement, canonical anchor, treatment). No default dropping.
NOTE_PLAN = {
    2: (("omit", "", "checkpoint objectives"),
        ("after", "fs-id1167833158753", "copy"),
        ("before", "fs-id1167833369424", "copy"),
        ("after", "fs-id1167833158753", "copy"),
        ("omit", "", "separate original practice, not source questions"),
        ("omit", "", "answers to separate original practice"),
        ("omit", "", "checkpoint transition")),
    3: (("after", "fs-id1167829711772", "copy"),),
    4: (("before", "fs-id1167833128978", "copy"),
        ("before", "fs-id1167836621459", "copy")),
    5: (("before", "fs-id1167829742787", "copy"),
        ("before", "fs-id1167836705606", "copy")),
    6: (),
    7: (("before", "fs-id1167829756267", "copy"),
        ("omit", "", "excerpt glossary exclusion no longer applies")),
    8: (("before", "fs-id1167829789538", "readiness-links"),
        ("after", "fs-id1167836538118", "copy"),
        ("before", "fs-id1167836629801", "last-paragraph"),
        ("before", "fs-id1167833057329", "copy")),
    9: (("after", "fs-id1167836601426", "local-links"),
        ("before", "fs-id1167829719636", "copy"),
        ("before", "fs-id1167836539582", "copy"),
        ("before", "fs-id1167836683566", "copy")),
    10: (("after", "fs-id1167829620795", "variable-roles"),
         ("before", "fs-id1167836388368", "local-formulas"),
         ("before", "fs-id1167829859398", "expression-inputs"),
         ("omit", "", "excerpt exclusion and transition no longer apply")),
    11: (("after", "fs-id1167836692527", "copy"),),
}
REWRITTEN_NOTES = {
    "readiness-links": "पुनरावलोकनाचे वरील तीन स्रोत-दुवे m81422 या आधीच्या इंग्रजी विभागाकडे जातात; त्यासाठी इंटरनेट लागते. त्या लक्ष्यांचा मराठी अनुवाद या एकत्रित मसुद्यात नाही. येथे नसलेला मजकूर ऑफलाइन उपलब्ध असल्याचा दावा नाही.",
    "local-links": "वरील तीन संदर्भ आता याच एकत्रित मराठी मसुद्यातील मूळ ओळखचिन्हांच्या लक्ष्यांकडे जातात. आधीच्या घटकांतील इंग्रजी स्रोत-दुवेही मागोव्यासाठी स्वतंत्र गुणधर्मात जतन केले आहेत.",
    "variable-roles": "‘कोणतेही मूल्य’ म्हणजे दिलेल्या प्रांतातील कोणतेही मूल्य. स्वतंत्र चल म्हटल्याने तो प्रत्यक्ष प्रयोगात आपल्या नियंत्रणात असतोच असे नाही. तसेच x बदलल्यावर y बदललाच पाहिजे, असा अवलंबी चल या शब्दाचा अर्थ नाही. मुख्य संकल्पनांनंतरच्या जोडस्पष्टीकरणात या भेदांची अधिक उजळणी आहे.",
    "local-formulas": "पुढील प्रत्येक प्रश्नात त्याच प्रश्नात दिलेले फलन वापरा; f हे नाव पुन्हा आले तरी सूत्र बदलू शकते. या सरावातील सूत्रांसाठी प्रांताची वेगळी मर्यादा दिलेली नाही; येथे नेहमीप्रमाणे वास्तविक संख्या आदान म्हणून घेतल्या आहेत.",
    "expression-inputs": "वरील सोडवलेल्या उदाहरणात f(a) हे अक्षरी आदानही आहे; त्यात फक्त संख्यात्मक आदाने होती असे मानू नका. पुढील उदाहरणात कंसातील संपूर्ण राशी ठेवणे आणि दोन फलन-मूल्यांची बेरीज करणे यांतील फरक स्पष्ट होतो.",
}


def text(node):
    return "".join(node.itertext()).strip()


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
    result = (base / candidate).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError("resolved path escapes language directory")
    return result


def signature(node):
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, sorted(node.attrib.items()), norm(node.text),
            [(signature(q), norm(q.tail)) for q in node])


def source_ids(node):
    return [n.get("id") for n in node.iter() if n.get("id")]


def unique_index(root):
    result = {}
    for node in root.iter():
        sid = node.get("id")
        if sid:
            if sid in result:
                raise ValueError("duplicate ID: " + sid)
            result[sid] = node
    return result


def make(tag, content=None, **attrs):
    node = ET.Element(tag, attrs)
    node.text = content
    return node


def stage_write(base, outputs):
    """Validate/calculate first, stage all bytes, then replace named outputs.

    Replacement of several paths is not an atomic multi-file transaction.
    A read/validation/staging failure leaves previous outputs untouched.
    """
    paths = [(safe_path(base, relative), raw) for relative, raw in outputs.items()]
    with tempfile.TemporaryDirectory(prefix=".m81373-", dir=base) as temporary:
        staged = []
        for i, (destination, raw) in enumerate(paths):
            path = Path(temporary) / str(i)
            path.write_bytes(raw)
            staged.append((path, destination))
        for path, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(path, destination)


def capture_source(base=BASE):
    outputs = {}
    for locale, (archive, member, digest, size, _) in SOURCE_PINS.items():
        # Bootstrap only: read two named members, never extract an archive.
        archive_path = base.parent / "downloads/mr-Deva-IN/releases" / archive
        with zipfile.ZipFile(archive_path) as handle:
            if sum(info.filename == member for info in handle.infolist()) != 1:
                raise ValueError("ambiguous source module member")
            raw = handle.read(member)
        if sha(raw) != digest or len(raw) != size:
            raise ValueError("pinned source member drift: " + locale)
        outputs[f"{SOURCE_DIR}/{locale}-m81373.cnxml"] = raw
    stage_write(base, outputs)
    return {path: {"sha256": sha(raw), "bytes": len(raw)} for path, raw in outputs.items()}


class Assembly:
    def __init__(self, base=BASE):
        self.base = Path(base)
        self.inputs, self.roots, self.configs, self.selected = {}, {}, {}, {}
        self.assets, self.note_log, self.link_log = {}, [], []
        self.before, self.after = defaultdict(list), defaultdict(list)
        self.expected_math = {}
        self.selection_signatures = {}
        self.sources = {}
        self.read("tools/assemble_m81373.py")
        for locale, (_, _, digest, size, _) in SOURCE_PINS.items():
            raw = self.read(f"{SOURCE_DIR}/{locale}-m81373.cnxml")
            if sha(raw) != digest or len(raw) != size:
                raise ValueError("raw source witness drift: " + locale)
            self.sources[locale] = ET.fromstring(raw)
        self.source = self.sources["en"]
        self.source_index = unique_index(self.source)
        self.canonical_ids = list(self.source_index)
        if len(self.canonical_ids) != 625 or self.canonical_ids != source_ids(self.sources["id"]):
            raise ValueError("complete EN/ID source identity/order drift")
        for locale, source in self.sources.items():
            metadata = source.find(C + "metadata")
            if text(metadata.find(MD + "content-id")) != "m81373" or text(metadata.find(MD + "uuid")) != UUID:
                raise ValueError("source metadata identity drift")
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

    def load_units(self):
        legacy_raw = self.read("translations/MR-BRIDGE-001.xml")
        if sha(legacy_raw) != LEGACY_SHA:
            raise ValueError("historical pilot drift")
        legacy = ET.fromstring(legacy_raw)
        legacy_selections = {n.get("id") for n in legacy.iter() if n.get("data-source", "").startswith("A20:m81373#")}
        if legacy_selections != set(REPLACED):
            raise ValueError("unexpected legacy replacement scope")
        counts = []
        for unit in UNITS:
            root = ET.fromstring(self.read(f"translations/{unit}.xml"))
            unique_index(root)
            self.roots[unit] = root
            config = self.read_json(f"units/{unit}.json")
            self.configs[unit] = config
            lock = self.read_json(f"provenance/{unit}.lock.json")
            if lock["unit"] != unit or lock["locale"] != "mr-Deva-IN":
                raise ValueError("unit lock identity mismatch")
            if root.get("lang") != "mr-Deva-IN":
                raise ValueError("translation locale mismatch")
            witnesses = {w["path"]: w["sha256"] for w in lock["witnesses"]}
            if len(witnesses) != len(lock["witnesses"]):
                raise ValueError("duplicate lock witness")
            for path, digest in witnesses.items():
                if sha(self.read(path)) != digest:
                    raise ValueError("frozen witness drift: " + path)
            locked = {s["target_id"]: s for s in lock["source_selections"]}
            if len(locked) != len(lock["source_selections"]):
                raise ValueError("duplicate locked selector")
            current = 0
            for node in root.iter():
                locator = node.get("data-source", "")
                if not locator.startswith("A20:m81373#"):
                    continue
                sid = locator.split("#")[1]
                if sid not in self.source_index or node.get("id") != sid or sid in self.selected:
                    raise ValueError("unknown, duplicate or mismatched selection: " + sid)
                if sid not in locked or locked[sid]["locator"] != locator:
                    raise ValueError("selection not frozen: " + sid)
                if [s["locale"] for s in locked[sid]["sources"]] != ["en", "id"]:
                    raise ValueError("selection locale provenance drift")
                for frozen in locked[sid]["sources"]:
                    locale = frozen["locale"]
                    if frozen["module_sha256"] != SOURCE_PINS[locale][2]:
                        raise ValueError("selection source pin drift")
                    raw = self.read(frozen["fragment_path"])
                    if sha(raw) != frozen["fragment_sha256"]:
                        raise ValueError("fragment hash drift")
                    original = next(n for n in self.sources[locale].iter() if n.get("id") == sid)
                    if signature(ET.fromstring(raw)) != signature(original):
                        raise ValueError("fragment differs from complete source")
                self.selected[sid] = (unit, node)
                current += 1
            counts.append(current)
        if tuple(counts) != EXPECTED_COUNTS or len(self.selected) != 134:
            raise ValueError("134-selector scope drift")
        if {sid for sid, (u, _) in self.selected.items() if u == "MR-BRIDGE-011"} != set(REPLACED):
            raise ValueError("011 is not the exact four-block replacement")
        covered = Counter(n.get("id") for sid in self.selected for n in self.source_index[sid].iter() if n.get("id"))
        if any(count != 1 for count in covered.values()):
            raise ValueError("overlapping selected subtrees")
        if set(self.canonical_ids) - covered.keys() != set(CONTEXTS) | WRAPPERS:
            raise ValueError("unaccounted canonical source gap")

    def copy(self, unit, node):
        cloned = deepcopy(node)
        cloned.tail = None
        cloned.set("data-origin-unit", unit)
        for item in cloned.iter():
            sid = item.get("id")
            if sid and sid not in self.source_index and not sid.startswith("mr-answer-fs-id"):
                item.set("data-origin-id", sid)
                item.set("id", unit + "--" + sid)
            key = item.get("data-check")
            if key:
                value = text(item)
                if self.configs[unit]["expected_math"].get(key) != value:
                    raise ValueError("math differs from reviewed unit config: " + unit + ":" + key)
                namespaced = unit + "::" + key
                if namespaced in self.expected_math:
                    raise ValueError("duplicate assembly math key")
                self.expected_math[namespaced] = value
                item.set("data-origin-check", key)
                item.set("data-check", namespaced)
            if item.tag == "a":
                href = item.get("href", "")
                if item.get("data-source-document") == "m81373":
                    target = item.get("data-source-target-id")
                    if target not in self.source_index:
                        raise ValueError("unknown same-module link target")
                    item.set("data-prior-href", href)
                    item.set("href", "#" + target)
                    old_label = item.text or ""
                    item.set("data-prior-label", old_label)
                    item.text = old_label.replace("घटक 08 मधील ", "याच मसुद्यातील ").replace(" (इंग्रजी स्रोत-दुवा)", "")
                    self.link_log.append({"unit": unit, "target": target, "old_href": href, "new_href": "#" + target})
                elif href.startswith("#"):
                    target = href[1:]
                    if target not in self.source_index and not target.startswith("mr-answer-fs-id"):
                        item.set("href", "#" + unit + "--" + target)
            if item.tag == "img":
                src = item.get("src", "")
                if not src.startswith("asset:"):
                    raise ValueError("unreviewed image route")
                name = src[6:]
                asset = self.configs[unit].get("assets", {}).get(name)
                if not asset:
                    raise ValueError("source image has no frozen canonical asset")
                raw = self.read(asset["path"])
                if sha(raw) != asset["sha256"]:
                    raise ValueError("canonical asset drift")
                item.set("data-origin-src", src)
                item.set("src", "../" + asset["path"])
                self.assets[asset["path"]] = {"sha256": sha(raw), "bytes": len(raw), "mime": asset["mime"]}
        return cloned

    def outer_notes(self, root):
        parents = {child: node for node in root.iter() for child in node}
        notes = []
        for node in root.iter():
            if node.get("data-kind") != "original":
                continue
            ancestors, current = [], node
            while current in parents:
                current = parents[current]
                ancestors.append(current)
            if any(n.tag == "header" or n.get("id") == "credits" or n.get("data-kind") == "original"
                   or n.get("data-source", "").startswith("A20:m81373#") for n in ancestors):
                continue
            notes.append(node)
        return notes

    def prepare_notes(self):
        for unit, root in self.roots.items():
            number = int(unit[-3:])
            notes = self.outer_notes(root)
            plan = NOTE_PLAN[number]
            if len(notes) != len(plan):
                raise ValueError("unreviewed outer authored note inventory: " + unit)
            for index, (node, (placement, anchor, treatment)) in enumerate(zip(notes, plan)):
                record = {"unit": unit, "outer_note_index": index, "input_xml_sha256": sha(ET.tostring(node)),
                          "placement": placement, "anchor": anchor, "treatment": treatment}
                self.note_log.append(record)
                if placement == "omit":
                    continue
                if treatment == "copy":
                    copied = self.copy(unit, node)
                elif treatment == "last-paragraph":
                    if len(node.findall("p")) != 2:
                        raise ValueError("mixed scope/domain note changed")
                    copied = self.copy(unit, node.findall("p")[-1])
                    copied.set("data-kind", "original")
                else:
                    copied = make("aside", **{"data-kind": "original", "data-origin-unit": unit,
                                             "data-assembly-treatment": treatment})
                    copied.append(make("p", REWRITTEN_NOTES[treatment]))
                (self.before if placement == "before" else self.after)[anchor].append(copied)
            # These three header asides are substantive, not excerpt scope.
            header_asides = root.findall("header/aside")
            expected = 1 if number in (4, 5, 6) else 0
            if len(header_asides) != expected:
                raise ValueError("unreviewed header clarification inventory")
            if expected:
                copied = self.copy(unit, header_asides[0])
                first = copied.find("p")
                prefixes = {4: "घटक 01 मधील व्याख्या आठवा: ", 5: "घटक 01–04 मधील अर्थ कायम आहेत: "}
                if number in prefixes:
                    if not (first.text or "").startswith(prefixes[number]):
                        raise ValueError("header clarification prefix drift")
                    first.text = first.text[len(prefixes[number]):]
                anchor = {4: "fs-id1167833041789", 5: "fs-id1167836513559", 6: "fs-id1167836714017"}[number]
                self.after[anchor].append(copied)
                self.note_log.append({"unit": unit, "header_aside": 0, "placement": "after", "anchor": anchor,
                                      "treatment": "retain substantive clarification; remove obsolete excerpt prefix if present"})

    def emit(self, source):
        sid = source.get("id")
        if sid in self.selected:
            unit, node = self.selected[sid]
            result = self.copy(unit, node)
            result.set("data-source-tag", source.tag.split("}")[-1])
            if sid == "fs-id1167833158753":
                self.restore_sylvia_table(result)
            self.selection_signatures[sid] = signature(result)
        elif sid in CONTEXTS or sid in WRAPPERS:
            result = make("section", id=sid, **{"data-kind": "source-context", "data-source-tag": "section"})
            if source.get("class"):
                result.set("data-source-class", source.get("class"))
            title = source.find(C + "title")
            if sid in CONTEXTS:
                unit, heading = CONTEXTS[sid]
                original_context = unique_index(self.roots[unit])[sid]
                if text(original_context.find("h2")) != heading:
                    raise ValueError("context heading drift")
            elif title is not None:
                if text(title) != "Practice Makes Perfect":
                    raise ValueError("unreviewed source wrapper title")
                heading = "सरावातून प्रावीण्य"
            else:
                heading = None
                result.set("aria-label", "स्रोताधारित सराव")
            if heading:
                result.append(make("h2", heading, **{"data-kind": "translation", "data-source-title": text(title)}))
            for child in source:
                if child.tag == C + "title":
                    continue
                for emitted in self.emit(child):
                    result.append(emitted)
        else:
            raise ValueError("unselected source content: " + str(sid) + " " + source.tag)
        return self.before[sid] + [result] + self.after[sid]

    def restore_sylvia_table(self, result):
        """Repair the historical002 condensed table in this new artifact only.

        Personally read EN/ID021a-d and both frozen source tables. The old unit
        attached021a's media ID to the problem formula and omitted its row.
        Keep that problem formula, restore its source media ID to solution row1,
        and restore all four rows and the explicit source instruction cells.
        """
        nodes = unique_index(result)
        formula = nodes["fs-id1167829850506"]
        if text(formula) != "N(t) = 75 + 10t":
            raise ValueError("Sylvia formula changed before assembly repair")
        del formula.attrib["id"]
        old_table = nodes["fs-id1167829709312"]
        paragraphs = list(old_table)
        if [n.get("id") for n in paragraphs] != ["fs-id1167832971244", "fs-id1167833270224", "fs-id1167833309949"]:
            raise ValueError("historical Sylvia table structure changed")
        old_table.clear()
        old_table.tag = "table"
        old_table.attrib.update({"id": "fs-id1167829709312", "data-kind": "adaptation",
                                "data-assembly-treatment": "restore-four-source-rows"})
        old_table.append(make("caption", "N(5) काढण्याच्या संपूर्ण स्रोत-पायऱ्या", **{"data-kind": "original"}))
        thead = ET.SubElement(old_table, "thead", {"data-kind": "original"})
        tr = ET.SubElement(thead, "tr")
        tr.extend([make("th", "स्पष्टीकरण", scope="col"), make("th", "गणना", scope="col")])
        body = ET.SubElement(old_table, "tbody")
        restored_formula = make("span", "N(t) = 75 + 10t", id="fs-id1167829850506", **{
            "class": "math", "data-check": "ASSEMBLY::sylvia-row-021a"})
        self.expected_math["ASSEMBLY::sylvia-row-021a"] = "N(t) = 75 + 10t"
        for index, equation in enumerate([restored_formula] + paragraphs):
            tr = ET.SubElement(body, "tr")
            instruction = ET.SubElement(tr, "td")
            if index == 1:
                instruction.text = "येथे "
                argument = make("span", "t = 5", **{"class": "math", "data-check": "ASSEMBLY::sylvia-input"})
                argument.tail = " ठेवा."
                instruction.append(argument)
                self.expected_math["ASSEMBLY::sylvia-input"] = "t = 5"
            elif index == 2:
                instruction.text = "सोपी करा."
            ET.SubElement(tr, "td").append(equation)
        # Restore the supplied task repetition, not the old moved instruction.
        paragraph = nodes["fs-id1167833347223"]
        paragraph.clear()
        paragraph.set("id", "fs-id1167833347223")
        paragraph.text = "(b) "
        value = make("span", "N(5)", **{"class": "math"})
        value.tail = " काढा. या उत्तराचा अर्थ स्पष्ट करा."
        paragraph.append(value)
        roles = nodes["fs-id1167829715385"]
        roles.text = "(a) न वाचलेल्या ईमेलची संख्या ही दिवसांच्या संख्येचे फलन आहे. " + (roles.text or "").removeprefix("(a) ")
        problem, solution = nodes["fs-id1167836533836"], nodes["fs-id1167829715383"]
        forward = make("p", **{"data-kind": "original"})
        forward.append(make("a", "स्रोत-उत्तर पाहा", href="#fs-id1167829715383"))
        problem.append(forward)
        back = make("p", **{"data-kind": "original"})
        back.append(make("a", "प्रश्नाकडे परत", href="#fs-id1167836533836"))
        solution.append(back)
        note = make("aside", **{"data-kind": "original", "data-assembly-treatment": "historical-002-fidelity-repair"})
        note.append(make("p", "एकत्रीकरणातील स्रोत-निष्ठेची नोंद: आधीच्या घटक 02 मध्ये मूळ तक्त्याची पहिली सूत्र-ओळ प्रश्नातील सूत्राशी एकत्र आली होती आणि तक्ता तीन गणना-परिच्छेदांत दिला होता. येथे मूळ चार रांगा, पहिल्या माध्यमाचे योग्य स्थान आणि ‘सोपी करा’ ही स्वतंत्र सूचना पुनर्स्थापित केली आहे. गणित, मूळ स्रोत किंवा ऐतिहासिक घटक 02 बदललेला नाही."))
        result.append(note)
        self.note_log.append({"unit": "MR-BRIDGE-002", "selector": "fs-id1167833158753",
                              "treatment": "restore canonical media ancestry, four source rows and explicit instructions; repeat supplied part-b task; preserve historical XML"})

    def build(self):
        self.prepare_notes()
        root = make("article", id=UNIT, lang="mr-Deva-IN", **{
            "data-source-document": "m81373", "data-source-uuid": UUID,
            "data-status": "assembled-translation-draft", "data-reader-accepted": "false"})
        header = ET.SubElement(root, "header")
        header.append(make("p", "A20 · Intermediate Algebra 2e · m81373", **{"class": "eyebrow"}))
        header.append(make("h1", "संबंध आणि फलने"))
        header.append(make("p", "स्रोताच्या क्रमातील एकत्रित अनुवाद-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, सराव, स्रोत-उत्तरे, स्वमूल्यमापन आणि शब्दसूची येथे एकत्र केली आहेत. नव्याने जोडलेली उत्तरे व स्पष्टीकरणे स्वतंत्रपणे चिन्हांकित आहेत. हा वाचकाच्या मांडणीला मान्यता मिळालेला दस्तऐवज नाही; संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा कार्यप्रवाह पूर्ण झाल्याचा दावा नाही.", **{"data-kind": "original"}))
        metadata = ET.SubElement(header, "dl", {"class": "source-metadata", "data-kind": "original"})
        for key, value in (("मूळ इंग्रजी शीर्षक", "Relations and Functions"), ("इंडोनेशियन शीर्षक", "Relasi dan Fungsi"),
                           ("स्रोत दस्तऐवज", "m81373"), ("स्रोत UUID", UUID)):
            metadata.append(make("dt", key)); metadata.append(make("dd", value))
        header.append(make("p", "घटक 02–11 मधील अनुवाद वापरले आहेत. घटक 11 हा घटक 01 मधील चार संक्षिप्त स्रोतभागांचा पूर्ण पर्याय आहे; त्यांची दुहेरी मोजणी केलेली नाही आणि जुना घटक बदललेला नाही. उदाहरण व सरावप्रश्नांचे स्थानिक क्रमांक आधीच्या घटकांतील आहेत, पुस्तकाच्या सार्वत्रिक क्रमांकांचे दावे नाहीत; मूळ ओळखचिन्हे आणि स्रोतक्रम निश्चित आहेत.", **{"data-kind": "original"}))
        objectives = ET.SubElement(root, "section", {"id": "assembly-objectives", "data-kind": "source-context"})
        objectives.append(make("h2", "या विभागाची उद्दिष्टे", **{"data-kind": "original"}))
        for child in self.source.find(C + "metadata").find(MD + "abstract"):
            objectives.extend(self.emit(child))
        content = ET.SubElement(root, "section", {"id": "assembly-content", "data-kind": "source-context"})
        for child in self.source.find(C + "content"):
            content.extend(self.emit(child))
        glossary = ET.SubElement(root, "section", {"id": "assembly-glossary", "data-kind": "source-context"})
        glossary.append(make("h2", "शब्दसूची", **{"data-kind": "original"}))
        for child in self.source.find(C + "glossary"):
            glossary.extend(self.emit(child))
        credits = ET.SubElement(root, "section", {"id": "assembly-credits", "data-kind": "original"})
        credits.append(make("h2", "स्रोत, श्रेय आणि मर्यादा"))
        credits.append(make("p", "OpenStax, Intermediate Algebra 2e: Lynn Marecek आणि Andrea Honeycutt Mathis. मूळ मालिकेच्या पायाभरणीसाठी Lynn Marecek आणि MaryAnne Anthony-Smith यांचे श्रेय कायम. प्रकाशक: OpenStax, Rice University. पिन केलेला इंग्रजी m81373 स्रोत आणि इंडोनेशियन v0.3.0-wip आवृत्ती, त्यांच्या मूळ नोंदींसह, वापरली आहे. अनुवाद व एकत्रीकरण: वापरकर्त्याच्या सूचनेवरील Codex-सहाय्यित मराठी कार्यप्रवाह."))
        license_note = make("p", "निवडक स्रोत व मराठी अनुकूलन: ")
        link = make("a", "CC BY-NC-SA 4.0", href="https://creativecommons.org/licenses/by-nc-sa/4.0/")
        link.tail = "; स्वतंत्र तृतीय-पक्ष सूचना कायम लागू आहेत. पिन केलेल्या मूळ सूचना आणि घटकनिहाय पुराव्यांची संचिका-स्थाने एकत्रीकरणाच्या पावतीत नोंदवली आहेत; ती या प्रकल्पाच्या संचिकांपासून सापेक्ष आहेत."
        license_note.append(link); credits.append(license_note)
        credits.append(make("p", "येथे जोडलेल्या 28 मूळ स्रोत-आकृत्या संबंधित घटकांच्या assets संचिकांत बदल न करता आहेत; इतर समीकरण-चित्रांचे मजकूर-प्रतिलेखन मूळ माध्यम-ओळखचिन्हांखाली आहे. इंग्रजी व इंडोनेशियन मूळ चित्रे पिन केलेल्या स्रोतांमध्ये असून त्यांचे हॅश आणि स्पष्ट स्रोत-दुरुस्त्या स्वतंत्र पुराव्यांत जतन आहेत. येथील बांधणीची तपासणी ही नवी संपूर्ण चित्र-वाचन किंवा गणित-तज्ज्ञ मान्यता नाही."))
        credits.append(make("p", "प्रांत व फलन यांचे संदर्भसाक्षांकित शब्दप्रयोग कायम आहेत. कक्षा हा साक्षांकित पर्याय असला तरी मूल्यसंच हा कार्यप्रवाहातील तात्पुरता शब्द येथे ठेवला आहे. ‘सरावातून प्रावीण्य’ हे या एकत्रीकरणासाठी नव्याने केलेले शीर्षक-भाषांतर आहे; तो शब्दसमूह संदर्भात तंतोतंत आढळल्याचा दावा नाही. मातृभाषिक गणित-शिक्षकाचे पुनरावलोकन, वाचकाचे HTML/PDF दृश्य-परीक्षण आणि पूर्ण कार्यप्रवाह-स्वीकृती अद्याप स्वतंत्र आहेत."))
        self.validate(root)
        ET.indent(root, space="  ")
        raw = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
        receipt = self.receipt(root, raw)
        # Fail if a concurrently edited input changed after its first read.
        for relative, record in self.inputs.items():
            if sha(safe_path(self.base, relative).read_bytes()) != record["sha256"]:
                raise ValueError("input changed before output: " + relative)
        return raw, json_bytes(receipt)

    def validate(self, root):
        target = unique_index(root)
        actual = [sid for sid in target if sid in self.source_index]
        if actual != self.canonical_ids:
            raise ValueError("canonical 625-ID order/preservation failed")
        for sid, original in self.source_index.items():
            if [n.get("id") for n in target[sid].iter() if n.get("id") in self.source_index] != source_ids(original):
                raise ValueError("canonical ancestry mismatch: " + sid)
        for sid, expected in self.selection_signatures.items():
            if signature(target[sid]) != expected:
                raise ValueError("selected translated content changed during assembly: " + sid)
        selectors = [n.get("id") for n in root.iter() if n.get("data-source", "").startswith("A20:m81373#")]
        if selectors != [sid for sid in self.canonical_ids if sid in self.selected]:
            raise ValueError("selector order/preservation failed")
        exercises = list(self.source.iter(C + "exercise"))
        solutions = list(self.source.iter(C + "solution"))
        unsupplied = [n for n in exercises if n.find(C + "solution") is None]
        if (len(exercises), len(solutions), len(unsupplied)) != (84, 55, 29):
            raise ValueError("source answer inventory drift")
        for source in exercises:
            current = target[source.get("id")]
            problem = source.find(C + "problem")
            if problem.get("id") not in source_ids(current):
                raise ValueError("exercise lost its original problem")
            supplied = source.find(C + "solution")
            answer_id = supplied.get("id") if supplied is not None else "mr-answer-" + source.get("id")
            if answer_id not in source_ids(current):
                raise ValueError("exercise answer detached or absent")
            if supplied is None and target[answer_id].get("data-kind") != "original":
                raise ValueError("authored answer mislabeled supplied")
            if supplied is not None and target[answer_id].get("data-kind") == "original":
                raise ValueError("supplied answer mislabeled authored")
        authored_ids = [sid for sid in target if sid.startswith("mr-answer-fs-id")]
        if set(authored_ids) != {"mr-answer-" + n.get("id") for n in unsupplied}:
            raise ValueError("new/omitted authored source answer")
        checks = {}
        for n in root.iter():
            if n.get("data-check"):
                key = n.get("data-check")
                if key in checks:
                    raise ValueError("duplicate math key")
                checks[key] = text(n)
            if n.tag == "a":
                href = n.get("href", "")
                if href.startswith("#"):
                    if href[1:] not in target or not text(n):
                        raise ValueError("unresolved local link: " + href)
                elif not href.startswith("https://"):
                    raise ValueError("unreviewed link scheme")
        if checks != self.expected_math:
            raise ValueError("assembly changed a checked mathematical string")
        links = [n for n in root.iter("a") if n.get("data-source-document")]
        if Counter((n.get("data-source-document"), n.get("data-source-target-id")) for n in links) != Counter(
                (n.get("document", "m81373"), n.get("target-id")) for n in self.source.iter(C + "link") if not n.get("url")):
            raise ValueError("source link identity/multiplicity drift")
        if len(self.link_log) != 3:
            raise ValueError("expected exactly three localized source references")
        for n in links:
            if n.get("data-source-document") == "m81422" and not n.get("href", "").startswith("https://"):
                raise ValueError("untranslated reference falsely localized")
        if sum(n.get("href") == "https://openstax.org/l/37introfunction" for n in root.iter("a")) != 1:
            raise ValueError("optional source resource missing")

    def receipt(self, root, raw):
        return {
            "schema": 1, "module": "A20:m81373", "status": "assembled_translation_draft",
            "reader_accepted": False, "full_workflow_complete": False,
            "output": {"path": OUTPUT, "sha256": sha(raw), "bytes": len(raw)},
            "source_metadata": {"content_id": "m81373", "uuid": UUID, "en_title": "Relations and Functions", "id_title": "Relasi dan Fungsi", "mr_title": "संबंध आणि फलने"},
            "source_members": {locale: {"path": f"{SOURCE_DIR}/{locale}-m81373.cnxml", "sha256": pin[2], "bytes": pin[3],
                                        "original_archive": "downloads/mr-Deva-IN/releases/" + pin[0], "original_member": pin[1],
                                        "recorded_archive_sha256": pin[4], "archive_required_for_default_rebuild": False}
                               for locale, pin in SOURCE_PINS.items()},
            "counts": {"canonical_ids": 625, "unique_selectors": 134, "source_exercises": 84,
                       "source_supplied_answers": 55, "authored_answers_to_source_omissions": 29,
                       "restored_legacy_nested_ids": 61, "restored_practice_wrapper_ids": 2,
                       "canonical_assets": len(self.assets), "math_checks": len(self.expected_math),
                       "localized_source_links": 3, "untranslated_external_source_links": 3, "optional_external_resources": 1},
            "replacement": {"old_unit": "MR-BRIDGE-001", "old_xml_sha256": LEGACY_SHA,
                            "chosen_unit": "MR-BRIDGE-011", "selectors": list(REPLACED), "new_unique_selectors": 0},
            "selection_order": [{"locator": "A20:m81373#" + sid, "unit": self.selected[sid][0]} for sid in self.canonical_ids if sid in self.selected],
            "canonical_id_order": self.canonical_ids,
            "context_headings": {**{sid: info[1] for sid, info in CONTEXTS.items()}, "fs-id1167826189010": "सरावातून प्रावीण्य"},
            "authored_note_dispositions": self.note_log, "localized_links": self.link_log,
            "assets": self.assets, "expected_math": self.expected_math,
            "inputs": dict(sorted(self.inputs.items())),
            "limits": ["No HTML/PDF generated or inspected; existing Browser denial remains in force.",
                       "Assembly preservation checks are not a fresh full semantic/pixel/math review or human approval.",
                       "Local labels remain unit-local; original IDs/order govern source identity.",
                       "Default rebuild does not read downloads or absolute donor paths.",
                       "Generated output replacements are staged but not an atomic multi-file transaction."],
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="recompute and compare without writing")
    mode.add_argument("--capture-source", action="store_true", help="bootstrap two exact small source members only")
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
        print("PASS: exact XML/receipt rebuild;625 source IDs,134 selections,84 exercises,55 supplied+29 authored answers")
    else:
        stage_write(BASE, outputs)
        print("WROTE assembled translation draft (not an accepted reader): " + sha(raw))


if __name__ == "__main__":
    main()
