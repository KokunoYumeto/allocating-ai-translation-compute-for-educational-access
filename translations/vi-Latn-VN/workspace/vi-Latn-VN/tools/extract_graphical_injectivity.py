"""Extract the final five Graphical exercises, after U012 and before Numeric."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
PARENT = "fs-id1165135664071"
START = "fs-id1165135531627"
PREVIOUS = "fs-id1165134325868"
LAST = "fs-id1165134394579"
STOP = "fs-id1165135342204"
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
    parent = next(n for n in original.iter() if n.get("id") == PARENT)
    siblings = next(list(n) for n in original.iter() if parent in list(n))
    assert siblings[siblings.index(parent) + 1].get("id") == STOP
    children = list(parent)
    start = next(i for i, n in enumerate(children) if n.get("id") == START)
    assert children[start - 1].get("id") == PREVIOUS
    assert children[-1].get("id") == LAST
    # U012 owns the Graphical parent ID/title.
    excerpt = ET.Element(f"{{{CN}}}source-excerpt")
    for child in children[start:]:
        excerpt.append(deepcopy(child))
    assert len(excerpt) == 6
    assert len(excerpt.findall(f"{{{CN}}}exercise")) == 5
    assert not list(excerpt.iter(f"{{{MATH}}}math"))
    return excerpt


def main():
    nodes = []
    for relative, expected in ORIGINALS:
        path = ROOT / relative
        assert sha256(path.read_bytes()).hexdigest() == expected, relative
        nodes.append(selected(path))
    identities = lambda n: [x.get("id") for x in n.iter() if x.get("id")]
    images = lambda n: [x.get("src") for x in n.iter(f"{{{CN}}}image")]
    assert identities(nodes[0]) == identities(nodes[1])
    assert images(nodes[0]) == images(nodes[1])
    data = ET.tostring(nodes[0], encoding="utf-8", xml_declaration=True)
    write_atomic(ROOT / "vi-Latn-VN/sources/m49301-graphical-injectivity-source.cnxml", data)
    print(f"Extracted {len(identities(nodes[0]))} IDs, 5 exercises, "
          f"{len(images(nodes[0]))} images, 0 MathML")
    print(f"SHA256 {sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
