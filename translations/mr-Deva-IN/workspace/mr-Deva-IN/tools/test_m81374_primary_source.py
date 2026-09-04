"""Independent source/integration oracle for the complete A20:m81374 draft.

This suite deliberately does not import ``assemble_m81374``.  It derives the
source contract from the two immutable raw witnesses and the released
MR-BRIDGE-012--022 XML/config/lock files, then checks the assembled XML and
receipt.  It is source-level QA only: no browser, HTML, PDF, accessibility,
native-speaker, teacher, or complete-book acceptance is implied.
"""

from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unicodedata
import unittest
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"
MODULE = "m81374"
ASSEMBLY = "A20-m81374"
UUID = "4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada"
UNITS = tuple(f"MR-BRIDGE-{number:03d}" for number in range(12, 23))
NONCANONICAL_IDS = {
    "A20-m81374", "assembly-objectives", "assembly-content",
    "MR-BRIDGE-015--MR-BRIDGE-015-self-rating", "credits",
}

RAW_PINS = {
    "en": ("provenance/A20-m81374-assembly/en-m81374.cnxml", 247327,
           "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": ("provenance/A20-m81374-assembly/id-m81374.cnxml", 247303,
           "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
ARCHIVE_PINS = {
    "en": ("downloads/mr-Deva-IN/releases/A20-canonical.zip",
           "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip",
           "source/modules/m81374/index.cnxml",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
ARTIFACT_PINS = {
    "translations/A20-m81374.xml": (588465, "c629adb12dd6381b9d219d783f4af055aa1a8c060a9b36dce3bfcb5a39c1172d"),
    "qa/A20-m81374-assembly-receipt.json": (333290, "b9ba76426ed17552d523f6ad192cbb11944efcd85483cfef88289c98f646df16"),
    "tools/assemble_m81374.py": (48826, "3220e1a0164c1a6af71066d3250952cc7773a70a1f6095c0a5fbc3548274b54d"),
    "tools/test_assemble_m81374.py": (19452, "fc564533efd30dbe33d1de50aae1acdae9abbb9fa50ca90857e768594013be00"),
}
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
EXPECTED_SELECTOR_COUNTS = (18, 47, 12, 63, 40, 50, 35, 21, 33, 31, 30)
WRAPPER_OWNERS = {
    "fs-id1167836579284": "MR-BRIDGE-012", "fs-id1167836522816": "MR-BRIDGE-013",
    "fs-id1167836386547": "MR-BRIDGE-014", "fs-id1167836310305": "MR-BRIDGE-015",
    "fs-id1167836300671": "MR-BRIDGE-015", "fs-id1167836602786": "MR-BRIDGE-015",
    "fs-id1167836524742": "MR-BRIDGE-016", "fs-id1167824674139": "MR-BRIDGE-016",
    "fs-id1167829740806": "MR-BRIDGE-017", "fs-id1167836526512": "MR-BRIDGE-018",
    "fs-id1167836570304": "MR-BRIDGE-019", "fs-id1167826172554": "MR-BRIDGE-020",
    "fs-id1167836699953": "MR-BRIDGE-021", "fs-id1167836628671": "MR-BRIDGE-022",
}
NOTE_PLAN = {
    "MR-BRIDGE-012": (("after", "fs-idm263727344"), ("after", "fs-id1167833386905")),
    "MR-BRIDGE-013": (("after", "fs-id1167836692114"), ("after", "fs-id1167826171267")),
    "MR-BRIDGE-014": (("after", "fs-id1167825884739"), ("after", "fs-id1167836515910")),
    "MR-BRIDGE-015": (("before", "fs-id1167836300671"), ("after", "fs-id1167833181234"),
                      ("after", "fs-id1167836356048"), ("after", "fs-id1167836356048"),
                      ("after", "fs-id1167836579171")),
    "MR-BRIDGE-016": (("before", "fs-id1167836689070"),),
    "MR-BRIDGE-017": (("before", "fs-id1167833047231"), ("after", "fs-id1167836540143"),
                      ("after", "fs-id1167836558141"), ("after", "fs-id1167833019834"),
                      ("after", "fs-id1167836527756")),
    "MR-BRIDGE-018": (("before", "fs-id1167836613250"), ("after", "fs-id1167829744040"),
                      ("after", "fs-id1167833086732")),
    "MR-BRIDGE-019": (("before", "fs-id1167832951212"), ("after", "fs-id1167824734423")),
    "MR-BRIDGE-020": (("before", "fs-id1167836486019"), ("after", "fs-id1167824736070")),
    "MR-BRIDGE-021": (("before", "fs-id1167836597214"),),
    "MR-BRIDGE-022": (("before", "fs-id1167833142400"),),
}
MISSING_ANSWER_TEXT = {
    "स्रोतात या प्रश्नाचे उत्तर दिलेले नाही. हा प्रश्न स्वतः सोडवण्यासाठी जतन केला आहे.",
    "स्रोतात या लेखनप्रश्नाचे उत्तर दिलेले नाही. तुमचे स्पष्टीकरण स्वतः लिहा.",
    "स्रोतात या प्रश्नाचे उत्तर दिलेले नाही. स्वतः सोडवा.",
}
EXPECTED_LOCALIZED_LINKS = {
    ("MR-BRIDGE-012", "CNX_IntAlg_Figure_03_06_001", "#CNX_IntAlg_Figure_03_06_001"),
    ("MR-BRIDGE-013", "CNX_IntAlg_Figure_03_06_001", "#CNX_IntAlg_Figure_03_06_001"),
    ("MR-BRIDGE-013", "CNX_IntAlg_Figure_03_06_007", "#CNX_IntAlg_Figure_03_06_007"),
    ("MR-BRIDGE-013", "fs-id1167836683384", "#fs-id1167836683384"),
    ("MR-BRIDGE-013", "fs-id1167832966170", "#fs-id1167832966170"),
    ("MR-BRIDGE-021", None, "#A20-m81374"),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(relative):
    return (BASE / relative).read_bytes()


def unique_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(relative):
    return json.loads(read(relative), object_pairs_hook=unique_pairs)


def text(node):
    return "".join(node.itertext()).strip()


def normalized_text(node):
    return " ".join(text(node).split())


def signature(node):
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, tuple(sorted(node.attrib.items())), norm(node.text),
            tuple((signature(child), norm(child.tail)) for child in node))


def math_source_signature(node):
    """Compare source MathML while allowing localized prose inside mtext."""
    norm = lambda value: " ".join((value or "").split())
    node_text = "" if node.tag == M + "mtext" else norm(node.text)
    return (node.tag, tuple(sorted(node.attrib.items())), node_text,
            tuple((math_source_signature(child), norm(child.tail)) for child in node))


def receipt_signature(node):
    """Reproduce the receipt field's documented repr/list serialization."""
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, sorted(node.attrib.items()), norm(node.text),
            [(receipt_signature(child), norm(child.tail)) for child in node])


def index_ids(root):
    result = {}
    for node in root.iter():
        identity = node.get("id")
        if identity:
            if identity in result:
                raise ValueError("duplicate ID: " + identity)
            result[identity] = node
    return result


def canonical_parent_map(root, canonical):
    result = {}
    def visit(node, nearest):
        identity = node.get("id")
        if identity in canonical:
            result[identity] = nearest
            nearest = identity
        for child in node:
            visit(child, nearest)
    visit(root, None)
    return result


def parent_map(root):
    return {child: parent for parent in root.iter() for child in parent}


def unit_selectors(root):
    return [node for node in root.iter()
            if node.get("data-source", "").startswith("A20:m81374#")]


def outer_authored_nodes(root):
    parents = parent_map(root)
    result = []
    for node in root.iter():
        if node.get("data-kind") != "original":
            continue
        ancestors = []
        current = node
        while current in parents:
            current = parents[current]
            ancestors.append(current)
        if any(ancestor.tag in {"header", "footer"}
               or ancestor.get("id") == "credits"
               or ancestor.get("data-kind") == "original"
               or ancestor.get("data-source", "").startswith("A20:m81374#")
               for ancestor in ancestors):
            continue
        result.append(node)
    return result


def restored_copy(node):
    """Undo only documented transport in the assembled target."""
    node = deepcopy(node)
    for current in node.iter():
        if current.get("data-origin-id"):
            current.set("id", current.get("data-origin-id"))
        if current.get("data-origin-check"):
            current.set("data-check", current.get("data-origin-check"))
        if current.get("data-origin-src"):
            current.set("src", current.get("data-origin-src"))
        if current.get("data-prior-href") is not None:
            current.set("href", current.get("data-prior-href"))
        elif current.tag == "a" and current.get("href", "").startswith("#MR-BRIDGE-"):
            current.set("href", "#" + current.get("href").split("--", 1)[1])
        for key in ("data-origin-unit", "data-origin-id", "data-origin-check", "data-origin-src",
                    "data-source-tag", "data-prior-href", "data-assembly-note",
                    "data-assembly-header-note"):
            current.attrib.pop(key, None)
    return node


def omission_nodes(node):
    result = []
    for item in node.iter():
        classes = item.get("class", "").split()
        if "source-answer-missing" in classes or (
                item.get("data-kind") == "original" and normalized_text(item) in MISSING_ANSWER_TEXT):
            result.append(item)
    return result


class PrimarySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = {locale: read(pin[0]) for locale, pin in RAW_PINS.items()}
        cls.sources = {locale: ET.fromstring(raw) for locale, raw in cls.raw_bytes.items()}
        cls.source_indices = {locale: index_ids(root) for locale, root in cls.sources.items()}
        cls.canonical_ids = list(cls.source_indices["en"])
        cls.canonical_set = set(cls.canonical_ids)
        cls.target_raw = read("translations/A20-m81374.xml")
        cls.target = ET.fromstring(cls.target_raw)
        cls.target_index = index_ids(cls.target)
        cls.receipt = read_json("qa/A20-m81374-assembly-receipt.json")
        cls.unit_roots, cls.configs, cls.locks = {}, {}, {}
        cls.selected = {}
        for unit in UNITS:
            cls.unit_roots[unit] = ET.fromstring(read(f"translations/{unit}.xml"))
            cls.configs[unit] = read_json(f"units/{unit}.json")
            cls.locks[unit] = read_json(f"provenance/{unit}.lock.json")
            for node in unit_selectors(cls.unit_roots[unit]):
                identity = node.get("data-source").split("#", 1)[1]
                if identity in cls.selected:
                    raise ValueError("duplicate selected identity: " + identity)
                cls.selected[identity] = (unit, node)
        cls.expected_checks = {
            f"{unit}::{key}": value
            for unit in UNITS for key, value in cls.configs[unit]["expected_math"].items()
        }
        cls.source_link_counter = Counter(
            (node.get("document", MODULE), node.get("target-id"))
            for node in cls.sources["en"].iter(C + "link") if not node.get("url")
        )

    def assert_file_pin(self, relative, pin):
        raw = read(relative)
        self.assertEqual((len(raw), sha(raw)), pin, relative)

    def assert_target_contract(self, root):
        target = index_ids(root)
        self.assertEqual(set(target), self.canonical_set | NONCANONICAL_IDS)
        actual = [identity for identity in target if identity in self.canonical_set]
        self.assertEqual(actual, self.canonical_ids)
        self.assertEqual(canonical_parent_map(root, self.canonical_set),
                         canonical_parent_map(self.sources["en"], self.canonical_set))
        selectors = [node.get("id") for node in root.iter()
                     if node.get("data-source", "").startswith("A20:m81374#")]
        self.assertEqual(selectors, [identity for identity in self.canonical_ids if identity in self.selected])
        self.assertEqual(len(selectors), 380)

        checks = {}
        for node in root.iter():
            key = node.get("data-check")
            if key:
                self.assertNotIn(key, checks)
                checks[key] = text(node)
        self.assertEqual(checks, self.expected_checks)

        exercises = list(self.sources["en"].iter(C + "exercise"))
        for source in exercises:
            current = target[source.get("id")]
            problem = source.find(C + "problem")
            solution = source.find(C + "solution")
            descendants = {item.get("id") for item in current.iter() if item.get("id")}
            self.assertIn(problem.get("id"), descendants)
            missing = omission_nodes(current)
            if solution is None:
                self.assertEqual(len(missing), 1)
                self.assertEqual(missing[0].get("data-kind"), "original")
            else:
                self.assertFalse(missing)
                self.assertIn(solution.get("id"), descendants)
                solution_node = target[solution.get("id")]
                self.assertIn("solution", solution_node.get("class", "").split())
                self.assertNotEqual(solution_node.get("data-kind"), "original")
                hrefs = [item.get("href") for item in current.iter("a")]
                self.assertIn("#" + solution.get("id"), hrefs)
                self.assertIn("#" + problem.get("id"), hrefs)

        images = list(root.iter("img"))
        source_names = [Path(node.get("src")).name for node in self.sources["en"].iter(C + "image")]
        self.assertEqual([node.get("data-origin-src", "").removeprefix("asset:") for node in images],
                         source_names)
        self.assertEqual(len(images), 149)
        for node in images:
            route = node.get("src", "")
            self.assertTrue(route.startswith("../assets/"))
            self.assertNotIn("..", Path(route).parts[1:])
            self.assertNotIn("\\", route)
            self.assertTrue(node.get("alt"))

        ids = set(target)
        annotated = [node for node in root.iter("a")
                     if node.get("data-source-document") is not None
                     or node.get("data-source-target-id") is not None]
        counter = Counter((node.get("data-source-document", MODULE),
                           node.get("data-source-target-id")) for node in annotated)
        self.assertEqual(counter, self.source_link_counter)
        for node in root.iter("a"):
            href = node.get("href", "")
            if href.startswith("#"):
                self.assertIn(href[1:], ids)
                self.assertTrue(normalized_text(node))
            else:
                self.assertTrue(href.startswith("https://"))

    def verify_receipt_input_map(self, inputs):
        self.assertEqual(len(inputs), 954)
        self.assertEqual(sum(record["bytes"] for record in inputs.values()), 13527010)
        for relative, record in inputs.items():
            self.assertFalse(Path(relative).is_absolute(), relative)
            self.assertNotIn("..", Path(relative).parts, relative)
            self.assertFalse(relative.startswith("downloads/"), relative)
            raw = read(relative)
            self.assertEqual((len(raw), sha(raw)), (record["bytes"], record["sha256"]), relative)

    def test_01_exact_artifact_unit_and_source_pins(self):
        for relative, pin in ARTIFACT_PINS.items():
            self.assert_file_pin(relative, pin)
        for locale, (relative, size, digest) in RAW_PINS.items():
            self.assert_file_pin(relative, (size, digest))
        for unit, pins in UNIT_PINS.items():
            for relative, pin in zip((f"translations/{unit}.xml", f"units/{unit}.json",
                                      f"provenance/{unit}.lock.json"), pins):
                self.assert_file_pin(relative, pin)

    def test_02_raw_sources_have_exact_metadata_structure_ids_and_math(self):
        for locale, root in self.sources.items():
            self.assertEqual(sum(1 for _ in root.iter()), 7223)
            self.assertEqual(list(self.source_indices[locale]), self.canonical_ids)
            metadata = root.find(C + "metadata")
            self.assertEqual(normalized_text(metadata.find(MD + "content-id")), MODULE)
            self.assertEqual(normalized_text(metadata.find(MD + "uuid")), UUID)
            self.assertEqual(len(list(root.iter(M + "math"))), 481)
        self.assertEqual(len(self.canonical_ids), 1366)
        self.assertEqual(canonical_parent_map(self.sources["en"], self.canonical_set),
                         canonical_parent_map(self.sources["id"], self.canonical_set))
        en_shape = [(node.tag.split("}")[-1], node.get("id")) for node in self.sources["en"].iter()]
        id_shape = [(node.tag.split("}")[-1], node.get("id")) for node in self.sources["id"].iter()]
        self.assertEqual(en_shape, id_shape)
        # The only permitted EN/ID MathML text differences are localized prose
        # in six mtext nodes; the tree, attributes, operators, numbers, and
        # identifiers remain exact.
        self.assertEqual([math_source_signature(node)
                          for node in self.sources["en"].iter(M + "math")],
                         [math_source_signature(node)
                          for node in self.sources["id"].iter(M + "math")])
        differing_tags = Counter()
        for en_math, id_math in zip(self.sources["en"].iter(M + "math"),
                                    self.sources["id"].iter(M + "math")):
            for en_node, id_node in zip(en_math.iter(), id_math.iter()):
                en_direct = " ".join((en_node.text or "").split())
                id_direct = " ".join((id_node.text or "").split())
                if en_direct != id_direct:
                    differing_tags[en_node.tag] += 1
        self.assertEqual(differing_tags, Counter({M + "mtext": 6}))

    def test_03_all_unit_locks_fragments_witnesses_configs_and_assets(self):
        expected_members = {locale: ARCHIVE_PINS[locale][1] for locale in ("en", "id")}
        expected_archives = {locale: ARCHIVE_PINS[locale][2] for locale in ("en", "id")}
        for unit, expected_count in zip(UNITS, EXPECTED_SELECTOR_COUNTS):
            root, config, lock = self.unit_roots[unit], self.configs[unit], self.locks[unit]
            selectors = unit_selectors(root)
            self.assertEqual(len(selectors), expected_count)
            self.assertEqual(config["source_count"], expected_count)
            self.assertEqual((lock["unit"], lock["locale"]), (unit, "mr-Deva-IN"))
            locked = lock["source_selections"]
            self.assertEqual([record["target_id"] for record in locked],
                             [node.get("id") for node in selectors])
            witnesses = {record["path"]: record for record in lock["witnesses"]}
            self.assertEqual(len(witnesses), len(lock["witnesses"]))
            for path, record in witnesses.items():
                raw = read(path)
                self.assertEqual((len(raw), sha(raw)), (record["bytes"], record["sha256"]), path)
            for record in locked:
                identity = record["target_id"]
                self.assertEqual(record["locator"], f"A20:m81374#{identity}")
                self.assertEqual([source["locale"] for source in record["sources"]], ["en", "id"])
                for source in record["sources"]:
                    locale = source["locale"]
                    self.assertEqual(source["module_sha256"], RAW_PINS[locale][2])
                    self.assertEqual(source["member"], expected_members[locale])
                    self.assertEqual(source["archive_sha256"], expected_archives[locale])
                    fragment = read(source["fragment_path"])
                    self.assertEqual(sha(fragment), source["fragment_sha256"])
                    parsed = ET.fromstring(fragment)
                    self.assertEqual(signature(parsed), signature(self.source_indices[locale][identity]))
                    math_hashes = [sha(ET.tostring(node, encoding="utf-8"))
                                   for node in self.source_indices[locale][identity].iter(M + "math")]
                    self.assertEqual(source["math_sha256"], math_hashes)
            for name, asset in config["assets"].items():
                raw = read(asset["path"])
                self.assertEqual(Path(asset["path"]).name, name)
                self.assertEqual(sha(raw), asset["sha256"])
                self.assertIn(asset["mime"], {"image/jpeg", "image/png"})

    def test_04_380_nonnested_selectors_cover_1352_ids_once_in_source_order(self):
        self.assertEqual(tuple(sum(1 for owner, _ in self.selected.values() if owner == unit)
                               for unit in UNITS), EXPECTED_SELECTOR_COUNTS)
        self.assertEqual(len(self.selected), 380)
        covered = Counter()
        for identity in self.selected:
            for node in self.source_indices["en"][identity].iter():
                if node.get("id"):
                    covered[node.get("id")] += 1
        self.assertEqual(set(covered.values()), {1})
        self.assertEqual(len(covered), 1352)
        self.assertEqual(self.canonical_set - set(covered), set(WRAPPER_OWNERS))
        selected_set = set(self.selected)
        for identity in selected_set:
            descendants = {node.get("id") for node in self.source_indices["en"][identity].iter()
                           if node is not self.source_indices["en"][identity] and node.get("id")}
            self.assertFalse(descendants & selected_set, identity)
        expected = [identity for identity in self.canonical_ids if identity in selected_set]
        actual = [node.get("id") for node in self.target.iter()
                  if node.get("data-source", "").startswith("A20:m81374#")]
        self.assertEqual(actual, expected)

    def test_05_every_selected_subtree_and_authored_role_is_exact_after_transport(self):
        for identity, (unit, original) in self.selected.items():
            self.assertEqual(signature(restored_copy(self.target_index[identity])), signature(original),
                             (unit, identity))
        # This subtree equality includes every nested translation/original/adaptation role.
        source_roles = Counter(node.get("data-kind") for unit, original in self.selected.values()
                               for node in original.iter() if node.get("data-kind"))
        target_roles = Counter(node.get("data-kind") for identity in self.selected
                               for node in self.target_index[identity].iter() if node.get("data-kind"))
        self.assertEqual(source_roles, target_roles)
        self.assertEqual(target_roles["adaptation"], 1)

    def test_06_exact_1366_id_order_and_canonical_ancestry(self):
        self.assert_target_contract(self.target)

    def test_07_fourteen_wrappers_and_single_chapter_review_shell(self):
        for identity, owner in WRAPPER_OWNERS.items():
            wrapper = self.target_index[identity]
            self.assertEqual(wrapper.tag, "section")
            self.assertEqual(wrapper.get("data-kind"), "source-context")
            self.assertEqual(wrapper.get("data-origin-unit"), owner)
            self.assertIsNone(wrapper.get("data-source"))
            headings = [node for node in wrapper if node.tag in {"h2", "h3", "h4", "h5", "h6"}]
            self.assertEqual(len(headings), 1)
            source_title = self.source_indices["en"][identity].find(C + "title")
            receipt = self.receipt["wrapper_policy"]["wrappers"][identity]
            self.assertEqual(receipt["source_title"], normalized_text(source_title))
            self.assertEqual(receipt["marathi_heading"], normalized_text(headings[0]))
        chapter_id = "fs-id1167836524742"
        chapter = self.target_index[chapter_id]
        source = self.source_indices["en"][chapter_id]
        expected_children = [node.get("id") for node in source if node.get("id")]
        actual_children = [node.get("id") for node in chapter if node.get("id") in WRAPPER_OWNERS]
        self.assertEqual(actual_children, expected_children)
        self.assertEqual([self.target_index[identity].get("data-origin-unit") for identity in actual_children],
                         list(UNITS[4:10]))
        self.assertEqual(sum(node.get("id") == chapter_id for node in self.target.iter()), 1)

    def test_08_all_26_outer_nodes_header_clarification_and_exact_placements(self):
        target_markers = {node.get("data-assembly-note"): node for node in self.target.iter()
                          if node.get("data-assembly-note")}
        self.assertEqual(len(target_markers), 26)
        receipt_records = {(record["unit"], record["outer_note_index"]): record
                           for record in self.receipt["outer_authored_node_dispositions"]}
        self.assertEqual(len(receipt_records), 26)
        target_parents = parent_map(self.target)
        for unit in UNITS:
            originals = outer_authored_nodes(self.unit_roots[unit])
            self.assertEqual(len(originals), len(NOTE_PLAN[unit]), unit)
            groups = defaultdict(list)
            for index, (original, (placement, anchor)) in enumerate(zip(originals, NOTE_PLAN[unit])):
                marker = f"{unit}:{index}"
                current = target_markers[marker]
                self.assertEqual(signature(restored_copy(current)), signature(original), marker)
                record = receipt_records[(unit, index)]
                self.assertEqual((record["placement"], record["anchor"], record["treatment"]),
                                 (placement, anchor, "retain complete node"))
                self.assertEqual(record["input_xml_sha256"], sha(ET.tostring(original)))
                self.assertEqual(record["output_signature_sha256"],
                                 sha(repr(receipt_signature(current)).encode("utf-8")))
                groups[(placement, anchor)].append(current)
            for (placement, anchor), notes in groups.items():
                anchor_node = self.target_index[anchor]
                parent = target_parents[anchor_node]
                self.assertTrue(all(target_parents[note] is parent for note in notes))
                children = list(parent)
                anchor_position = children.index(anchor_node)
                note_positions = [children.index(note) for note in notes]
                expected_positions = (list(range(anchor_position - len(notes), anchor_position))
                                      if placement == "before"
                                      else list(range(anchor_position + 1, anchor_position + 1 + len(notes))))
                self.assertEqual(note_positions, expected_positions)
        header_notes = [node for node in self.target.iter() if node.get("data-assembly-header-note")]
        self.assertEqual(len(header_notes), 1)
        original = self.unit_roots["MR-BRIDGE-013"].find("header/aside")
        self.assertEqual(signature(restored_copy(header_notes[0])), signature(original))
        parent = target_parents[header_notes[0]]
        anchor = self.target_index["list-00001"]
        self.assertIs(target_parents[anchor], parent)
        self.assertEqual(list(parent).index(header_notes[0]), list(parent).index(anchor) + 1)

    def test_09_255_exercises_141_supplied_114_honest_omissions(self):
        exercises = list(self.sources["en"].iter(C + "exercise"))
        self.assertEqual(len(exercises), 255)
        self.assertEqual(len(list(self.sources["en"].iter(C + "solution"))), 141)
        supplied = omitted = 0
        for exercise in exercises:
            target = self.target_index[exercise.get("id")]
            solution = exercise.find(C + "solution")
            missing = omission_nodes(target)
            if solution is None:
                omitted += 1
                self.assertEqual(len(missing), 1)
                self.assertEqual(missing[0].get("data-kind"), "original")
            else:
                supplied += 1
                self.assertFalse(missing)
                solution_node = self.target_index[solution.get("id")]
                self.assertIn("solution", solution_node.get("class", "").split())
                self.assertNotEqual(solution_node.get("data-kind"), "original")
        self.assertEqual((supplied, omitted), (141, 114))
        self.assertFalse(any(identity.startswith("mr-answer-") for identity in self.target_index))

    def test_10_481_source_mathml_and_all_685_config_checks(self):
        self.assertEqual(len(list(self.sources["en"].iter(M + "math"))), 481)
        checks = {node.get("data-check"): text(node) for node in self.target.iter()
                  if node.get("data-check")}
        self.assertEqual(len(checks), 685)
        self.assertEqual(checks, self.expected_checks)
        self.assertEqual(checks, self.receipt["expected_math"])
        self.assertEqual(checks["MR-BRIDGE-013::all-reals"], "(−∞, ∞)")
        self.assertEqual(checks["MR-BRIDGE-013::nonnegative"], "[0, ∞)")

    def test_11_149_assets_exact_order_bytes_routes_and_receipt(self):
        source_names = [Path(node.get("src")).name for node in self.sources["en"].iter(C + "image")]
        self.assertEqual(len(source_names), 149)
        self.assertEqual(len(set(source_names)), 149)
        self.assertEqual(source_names,
                         [Path(node.get("src")).name for node in self.sources["id"].iter(C + "image")])
        target_images = list(self.target.iter("img"))
        self.assertEqual([node.get("data-origin-src").removeprefix("asset:") for node in target_images],
                         source_names)
        expected_assets = {}
        for unit in UNITS:
            for asset in self.configs[unit]["assets"].values():
                raw = read(asset["path"])
                expected_assets[asset["path"]] = {
                    "sha256": sha(raw), "bytes": len(raw), "mime": asset["mime"]}
        self.assertEqual(len(expected_assets), 149)
        self.assertEqual(sum(record["bytes"] for record in expected_assets.values()), 9908130)
        self.assertEqual(self.receipt["assets"], expected_assets)
        for image in target_images:
            relative = image.get("src").removeprefix("../")
            self.assertIn(relative, expected_assets)
            self.assertTrue(image.get("alt"))

    def test_12_blank_ratings_and_two_disclosed_linear_table_adaptations(self):
        ratings = [node for node in self.target.iter("table")
                   if node.get("data-origin-id") == "MR-BRIDGE-015-self-rating"]
        self.assertEqual(len(ratings), 1)
        cells = list(ratings[0].iter("td"))
        self.assertEqual(len(cells), 9)
        self.assertTrue(all(not cell.attrib and len(cell) == 0 and not normalized_text(cell)
                            for cell in cells))
        policies = {record["source_table_id"]: record for record in self.receipt["table_adaptations"]}
        expected = {"fs-id1167836688758": (4, 8), "fs-id1167836560655": (3, 6)}
        totals = [0, 0]
        for identity, (rows, entries) in expected.items():
            source = self.source_indices["en"][identity]
            target = self.target_index[identity]
            self.assertEqual((len(list(source.iter(C + "row"))), len(list(source.iter(C + "entry")))),
                             (rows, entries))
            self.assertEqual(target.tag, "div")
            self.assertFalse(list(target.iter("table")))
            self.assertEqual((policies[identity]["source_rows"], policies[identity]["source_entries"]),
                             (rows, entries))
            totals[0] += rows; totals[1] += entries
        self.assertEqual(tuple(totals), (7, 14))
        self.assertIn("m = −2", text(self.target_index["fs-id1167836688758"]))
        self.assertIn("b = −4", text(self.target_index["fs-id1167836688758"]))
        self.assertIn("(0, 4)", text(self.target_index["fs-id1167836560655"]))

    def test_13_six_localized_eight_external_source_links_and_safe_routes(self):
        annotated = [node for node in self.target.iter("a")
                     if node.get("data-source-document") is not None
                     or node.get("data-source-target-id") is not None]
        local = [node for node in annotated if node.get("data-source-document", MODULE) == MODULE]
        external = [node for node in annotated if node.get("data-source-document", MODULE) != MODULE]
        self.assertEqual((len(local), len(external)), (6, 8))
        actual_local = set()
        parents = parent_map(self.target)
        for node in local:
            current = node
            unit = None
            while current in parents and unit is None:
                current = parents[current]
                unit = current.get("data-origin-unit")
            actual_local.add((unit, node.get("data-source-target-id"), node.get("href")))
            self.assertTrue(node.get("href").startswith("#"))
            self.assertIsNotNone(node.get("data-prior-href"))
        self.assertEqual(actual_local, EXPECTED_LOCALIZED_LINKS)
        self.assertTrue(all(node.get("href", "").startswith("https://") for node in external))
        self.assertEqual(sum(node.get("href") == "https://openstax.org/l/37domainrange"
                             for node in self.target.iter("a")), 1)
        self.assertEqual(Counter((node.get("data-source-document", MODULE),
                                  node.get("data-source-target-id")) for node in annotated),
                         self.source_link_counter)

    def test_14_one_synthesized_header_footer_and_explicit_nonacceptance(self):
        self.assertEqual(len(self.target.findall("header")), 1)
        self.assertEqual(len(self.target.findall("footer")), 1)
        self.assertEqual(self.target.find("footer").get("id"), "credits")
        self.assertEqual(sum(node.get("id") == "credits" for node in self.target.iter()), 1)
        self.assertEqual(normalized_text(self.target.find("header/h1")), "फलनांचे आलेख")
        self.assertEqual((self.target.get("data-status"), self.target.get("data-reader-accepted")),
                         ("assembled-translation-draft", "false"))
        footer_text = normalized_text(self.target.find("footer"))
        self.assertIn("CC BY-NC-SA 4.0", footer_text)
        self.assertIn("HTML/PDF", footer_text)
        self.assertIn("मातृभाषिक/मानवी गणित-शिक्षक", footer_text)
        self.assertFalse(self.receipt["reader_accepted"])
        self.assertFalse(self.receipt["pdf_generated"])
        self.assertFalse(self.receipt["full_workflow_complete"])
        self.assertEqual(len(self.receipt["header_policy"]["unit_header_dispositions"]), 11)
        self.assertEqual(len(self.receipt["footer_policy"]["unit_footer_dispositions"]), 11)
        for unit in UNITS:
            root = self.unit_roots[unit]
            header, footer = root.find("header"), root.find("footer")
            hrecord = next(record for record in self.receipt["header_policy"]["unit_header_dispositions"]
                           if record["unit"] == unit)
            frecord = next(record for record in self.receipt["footer_policy"]["unit_footer_dispositions"]
                           if record["unit"] == unit)
            self.assertEqual(hrecord["input_xml_sha256"], sha(ET.tostring(header)))
            self.assertEqual(frecord["input_xml_sha256"], sha(ET.tostring(footer)))

    def test_15_complete_receipt_is_derived_and_every_input_pin_is_live(self):
        self.assertEqual(list(self.receipt), [
            "schema", "module", "status", "reader_accepted", "pdf_generated",
            "full_workflow_complete", "output", "source_metadata", "source_members", "counts",
            "selection_order", "canonical_id_order", "wrapper_policy",
            "outer_authored_node_dispositions", "table_adaptations", "link_policy",
            "header_policy", "footer_policy", "role_policy", "assets", "expected_math", "inputs",
            "limits"])
        self.assertEqual(self.receipt["output"], {
            "path": "translations/A20-m81374.xml", "sha256": sha(self.target_raw),
            "bytes": len(self.target_raw)})
        self.assertEqual(self.receipt["canonical_id_order"], self.canonical_ids)
        self.assertEqual(self.receipt["selection_order"], [
            {"locator": f"A20:m81374#{identity}", "unit": self.selected[identity][0]}
            for identity in self.canonical_ids if identity in self.selected])
        self.assertEqual(self.receipt["counts"], {
            "source_elements_per_locale": 7223, "canonical_ids": 1366,
            "unique_ordered_nonnested_selectors": 380, "rebuilt_source_wrappers": 14,
            "outer_authored_nodes_retained": 26, "source_exercises": 255,
            "source_supplied_answers": 141, "explicit_source_answer_omissions": 114,
            "source_mathml": 481, "namespaced_target_checks": 685,
            "canonical_assets": 149, "canonical_asset_bytes": 9908130,
            "blank_self_rating_cells": 9, "adapted_linear_source_tables": 2,
            "adapted_linear_source_rows": 7, "adapted_linear_source_entries": 14,
            "localized_same_module_source_links": 6,
            "external_outside_module_source_links": 8, "optional_external_resources": 1})
        expected_inputs = {"tools/assemble_m81374.py", *(pin[0] for pin in RAW_PINS.values())}
        for unit in UNITS:
            expected_inputs.update({f"translations/{unit}.xml", f"units/{unit}.json",
                                    f"provenance/{unit}.lock.json"})
            expected_inputs.update(record["path"] for record in self.locks[unit]["witnesses"])
            expected_inputs.update(source["fragment_path"]
                                   for record in self.locks[unit]["source_selections"]
                                   for source in record["sources"])
            expected_inputs.update(asset["path"] for asset in self.configs[unit]["assets"].values())
        self.assertEqual(set(self.receipt["inputs"]), expected_inputs)
        self.verify_receipt_input_map(self.receipt["inputs"])
        self.assertEqual(len(self.receipt["limits"]), 5)

    def test_16_marathi_integration_unicode_and_role_disclosures(self):
        decoded = self.target_raw.decode("utf-8")
        self.assertEqual(decoded, unicodedata.normalize("NFC", decoded))
        self.assertNotIn("\ufffd", decoded)
        self.assertNotIn("file://", decoded)
        self.assertNotIn("C:\\", decoded)
        selectors = [node for node in self.target.iter()
                     if node.get("data-source", "").startswith("A20:m81374#")]
        self.assertTrue(all(node.get("data-kind") == "translation" for node in selectors))
        self.assertTrue(all(node.get("data-origin-unit") in UNITS for node in selectors))
        self.assertGreater(sum("\u0900" <= char <= "\u097f" for char in decoded), 10000)
        roles = Counter(node.get("data-kind") for node in self.target.iter() if node.get("data-kind"))
        self.assertEqual(roles, Counter({"translation": 380, "original": 340,
                                         "source-context": 16, "adaptation": 1}))

    def test_17_default_check_rebuild_is_exact_and_archive_free(self):
        before = {path: read(path) for path in (
            "translations/A20-m81374.xml", "qa/A20-m81374-assembly-receipt.json")}
        result = subprocess.run(
            [sys.executable, "-B", str(BASE / "tools/assemble_m81374.py"), "--check"],
            cwd=BASE.parent, capture_output=True, text=True, timeout=180, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: exact m81374 XML/receipt rebuild", result.stdout)
        self.assertEqual({path: read(path) for path in before}, before)
        self.assertTrue(all(not path.startswith("downloads/") for path in self.receipt["inputs"]))

    def test_18_mutations_missing_duplicate_reorder_and_ancestry_fail(self):
        missing = deepcopy(self.target)
        next(node for node in missing.iter() if node.get("id") == self.canonical_ids[100]).set("id", "missing")
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(missing)
        duplicate = deepcopy(self.target)
        duplicate.find(".//*[@id='assembly-content']").append(
            ET.Element("p", {"id": self.canonical_ids[100]}))
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(duplicate)
        extra = deepcopy(self.target)
        extra.find(".//*[@id='assembly-content']").append(
            ET.Element("p", {"id": "unexpected-extra"}))
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(extra)
        reordered = deepcopy(self.target)
        content = reordered.find(".//*[@id='assembly-content']")
        first, second = content[0], content[1]
        content.remove(first); content.remove(second)
        content.insert(0, second); content.insert(1, first)
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(reordered)
        reparented = deepcopy(self.target)
        target = next(node for node in reparented.iter() if node.get("id") == self.canonical_ids[200])
        parents = parent_map(reparented)
        parents[target].remove(target)
        reparented.find(".//*[@id='assembly-content']").append(target)
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(reparented)

    def test_19_mutations_answer_role_math_image_link_and_pin_fail(self):
        role_drift = deepcopy(self.target)
        exercise = next(node for node in self.sources["en"].iter(C + "exercise")
                        if node.find(C + "solution") is not None)
        solution_id = exercise.find(C + "solution").get("id")
        next(node for node in role_drift.iter() if node.get("id") == solution_id).set(
            "data-kind", "original")
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(role_drift)
        supplied = deepcopy(self.target)
        current = next(node for node in supplied.iter() if node.get("id") == exercise.get("id"))
        link = next(node for node in current.iter("a") if node.get("href") == "#" + solution_id)
        parent_map(current)[link].remove(link)
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(supplied)
        omitted = deepcopy(self.target)
        exercise = next(node for node in self.sources["en"].iter(C + "exercise")
                        if node.find(C + "solution") is None)
        current = next(node for node in omitted.iter() if node.get("id") == exercise.get("id"))
        omission_nodes(current)[0].text = "उत्तर भरलेले आहे."
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(omitted)
        changed_math = deepcopy(self.target)
        next(node for node in changed_math.iter() if node.get("data-check")).text = "drift"
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(changed_math)
        changed_image = deepcopy(self.target)
        next(changed_image.iter("img")).set("src", "../assets/../../escape.jpg")
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(changed_image)
        changed_link = deepcopy(self.target)
        next(changed_link.iter("a")).set("href", "file:///private")
        with self.assertRaises((AssertionError, ValueError)):
            self.assert_target_contract(changed_link)
        changed_inputs = deepcopy(self.receipt["inputs"])
        first = next(iter(changed_inputs))
        changed_inputs[first]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            self.verify_receipt_input_map(changed_inputs)

    def test_20_duplicate_json_keys_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"a": 1, "a": 2}', object_pairs_hook=unique_pairs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
