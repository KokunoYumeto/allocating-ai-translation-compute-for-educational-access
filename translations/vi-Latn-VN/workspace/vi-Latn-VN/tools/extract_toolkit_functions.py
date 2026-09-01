"""Extract the complete nine-function toolkit section, stopping before Key Equations."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTION = "fs-id1165135545919"
STOP = "fs-id1165135203679"
ET.register_namespace("", CN)
ET.register_namespace("m", MATH)


def selected(path):
    content = list(ET.parse(path).getroot().find(f"{{{CN}}}content"))
    position = next(i for i, node in enumerate(content) if node.get("id") == SECTION)
    assert content[position + 1].get("id") == STOP
    return content[position]


def math_serials(node):
    result = []
    for math in node.iter(f"{{{MATH}}}math"):
        copied = deepcopy(math)
        copied.tail = None
        result.append(ET.tostring(copied))
    return result


def main():
    english = selected(ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    indonesian = selected(ROOT / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml")
    identities = lambda node: [n.get("id") for n in node.iter() if n.get("id")]
    assert identities(english) == identities(indonesian)
    assert math_serials(english) == math_serials(indonesian)
    output = ROOT / "vi-Latn-VN/sources/m49301-toolkit-functions-source.cnxml"
    write_atomic(output, ET.tostring(english, encoding="utf-8", xml_declaration=True))
    print(f"Extracted {len(identities(english))} source IDs, {len(math_serials(english))} MathML expressions")


if __name__ == "__main__":
    main()
