"""Extract Algebraic blocks A3-A6; original full EN/ID downloads are required."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
PARENT = "fs-id1165134080937"
START = "fs-id1165134066606"
PREVIOUS = "fs-id1165137599984"
LAST = "fs-id1165137433542"
STOP = "fs-id1165135664071"
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
    parent = original.find(f".//*[@id='{PARENT}']")
    siblings = next(list(n) for n in original.iter() if parent in list(n))
    position = siblings.index(parent)
    assert siblings[position + 1].get("id") == STOP
    children = list(parent)
    start = next(i for i, n in enumerate(children) if n.get("id") == START)
    assert children[start - 1].get("id") == PREVIOUS
    assert children[-1].get("id") == LAST
    # U010 owns the Algebraic section ID/title; do not duplicate either here.
    excerpt = ET.Element(f"{{{CN}}}source-excerpt")
    for child in children[start:]:
        excerpt.append(deepcopy(child))
    assert len(excerpt) == 14
    assert len(excerpt.findall(f"{{{CN}}}exercise")) == 13
    return excerpt


def math_serials(node):
    result = []
    for math in node.iter(f"{{{MATH}}}math"):
        copied = deepcopy(math)
        copied.tail = None
        result.append(ET.tostring(copied))
    return result


def main():
    nodes = []
    for relative, expected in ORIGINALS:
        path = ROOT / relative
        assert sha256(path.read_bytes()).hexdigest() == expected, relative
        nodes.append(selected(path))
    identities = lambda n: [x.get("id") for x in n.iter() if x.get("id")]
    assert identities(nodes[0]) == identities(nodes[1])
    assert math_serials(nodes[0]) == math_serials(nodes[1])
    output = ROOT / "vi-Latn-VN/sources/m49301-algebraic-evaluation-source.cnxml"
    data = ET.tostring(nodes[0], encoding="utf-8", xml_declaration=True)
    write_atomic(output, data)
    print(f"Extracted {len(identities(nodes[0]))} IDs, "
          f"{len(math_serials(nodes[0]))} MathML expressions, 13 exercises")
    print(f"SHA256 {sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
