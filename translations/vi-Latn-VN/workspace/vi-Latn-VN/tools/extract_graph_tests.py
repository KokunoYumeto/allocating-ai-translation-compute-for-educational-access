"""Extract both adjacent line-test sections without incorporating the next section."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTIONS = ("fs-id1165135435781", "fs-id1165137610952")
STOP = "fs-id1165135545919"
ET.register_namespace("", CN)
ET.register_namespace("m", MATH)


def extract(path):
    tree = ET.parse(path)
    content = tree.find(f"{{{CN}}}content")
    children = list(content)
    start = next(i for i, node in enumerate(children) if node.get("id") == SECTIONS[0])
    assert tuple(node.get("id") for node in children[start:start + 2]) == SECTIONS
    assert children[start + 2].get("id") == STOP
    wrapper = ET.Element("source-excerpt", {"module": "m49301", "stop-before": STOP})
    for node in children[start:start + 2]:
        wrapper.append(deepcopy(node))
    return wrapper


def main():
    english = extract(ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    indonesian = extract(ROOT / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml")
    ids = lambda root: [n.get("id") for n in root.iter() if n.get("id")]
    assert ids(english) == ids(indonesian)
    math_bytes = lambda root: [ET.tostring(n) for n in root.iter(f"{{{MATH}}}math")]
    # Compare MathML itself, excluding translated prose in element tails.
    def math_nodes(root):
        result = []
        for node in root.iter(f"{{{MATH}}}math"):
            copied = deepcopy(node)
            copied.tail = None
            result.append(ET.tostring(copied))
        return result
    assert math_nodes(english) == math_nodes(indonesian)
    output = ROOT / "vi-Latn-VN/sources/m49301-graph-tests-source.cnxml"
    write_atomic(output, ET.tostring(english, encoding="utf-8", xml_declaration=True))
    print(f"Extracted {len(ids(english))} source IDs and {len(math_bytes(english))} unchanged MathML expressions")


if __name__ == "__main__":
    main()
