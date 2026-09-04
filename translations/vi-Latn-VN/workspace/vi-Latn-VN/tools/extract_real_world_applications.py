"""Extract the complete final Real-World Applications exercise category."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTION = "fs-id1165135580349"
ORIGINALS = (
    ("downloads/upstream-openstax/modules/m49301/index.cnxml",
     "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612"),
    ("downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml",
     "67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a"),
)
ET.register_namespace("", CN)
ET.register_namespace("m", MATH)


def selected(path):
    original = ET.parse(path).getroot()
    section = next(n for n in original.iter() if n.get("id") == SECTION)
    parent = next(n for n in original.iter() if section in list(n))
    assert list(parent)[-1] is section
    assert list(parent)[-2].get("id") == "fs-id1165134373511"
    content = original.find(f"{{{CN}}}content")
    assert list(content)[-1] is parent
    assert list(original)[list(original).index(content) + 1].tag == f"{{{CN}}}glossary"
    glossary = original.find(f"{{{CN}}}glossary")
    assert glossary[0].get("id") == "fs-id1165137758543"
    exercises = section.findall(f"{{{CN}}}exercise")
    assert [n.get("id") for n in exercises] == [
        "fs-id1165135580355", "fs-id1165137922382", "fs-id1165135553615",
        "fs-id1165134272734", "fs-id1165135708043",
    ]
    return deepcopy(section)


def math_serials(node):
    result = []
    for math in node.iter(f"{{{MATH}}}math"):
        copied = deepcopy(math)
        copied.tail = None
        result.append(ET.tostring(copied))
    return result


def main():
    nodes = []
    for relative, digest in ORIGINALS:
        path = ROOT / relative
        assert sha256(path.read_bytes()).hexdigest() == digest, relative
        nodes.append(selected(path))
    identities = lambda n: [x.get("id") for x in n.iter() if x.get("id")]
    assert identities(nodes[0]) == identities(nodes[1])
    assert math_serials(nodes[0]) == math_serials(nodes[1])
    data = ET.tostring(nodes[0], encoding="utf-8", xml_declaration=True)
    write_atomic(ROOT / "vi-Latn-VN/sources/m49301-real-world-applications-source.cnxml", data)
    print(f"Extracted {len(identities(nodes[0]))} IDs, {len(math_serials(nodes[0]))} MathML, "
          "5 exercises; stopped before the glossary")
    print(f"SHA256 {sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
