"""Extract Numeric category, omitting exactly the three exercises owned by U001."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTION = "fs-id1165135342204"
STOP = "fs-id1165134373511"
OMIT = ("fs-id1165133324915", "fs-id1165135245507", "fs-id1165135381342")
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
    parent = next(n for n in original.iter() if n.get("id") == SECTION)
    siblings = next(list(n) for n in original.iter() if parent in list(n))
    assert siblings[siblings.index(parent) + 1].get("id") == STOP
    exercises = parent.findall(f"{{{CN}}}exercise")
    assert len(exercises) == 16
    assert tuple(n.get("id") for n in exercises[:3]) == OMIT
    assert exercises[3].get("id") == "fs-id1165137644802"
    assert exercises[-1].get("id") == "fs-id1165134086037"
    copied = deepcopy(parent)
    for child in list(copied):
        if child.get("id") in OMIT:
            copied.remove(child)
    assert len(copied.findall(f"{{{CN}}}exercise")) == 13
    return copied


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
    write_atomic(ROOT / "vi-Latn-VN/sources/m49301-numeric-exercises-source.cnxml", data)
    print(f"Extracted {len(identities(nodes[0]))} IDs, {len(math_serials(nodes[0]))} MathML, "
          "13 exercises; retained category/title and all shared prompts")
    print(f"SHA256 {sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
