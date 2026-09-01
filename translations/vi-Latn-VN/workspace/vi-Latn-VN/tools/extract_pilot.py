"""Extract a bounded translation input, not a training dataset. No network use."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
ET.register_namespace("", CN)
ET.register_namespace("m", "http://www.w3.org/1998/Math/MathML")
ET.register_namespace("md", "http://cnx.rice.edu/mdml")
source = ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml"
tree = ET.parse(source)
by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}
out = ET.Element(f"{{{CN}}}document", {"source-module": "m49301", "scope": "pilot-excerpt"})
ET.SubElement(out, f"{{{CN}}}title").text = "Functions: relation/function prerequisite excerpt"
content = ET.SubElement(out, f"{{{CN}}}content")
content.append(deepcopy(by_id["fs-id1165137431376"]))
section = deepcopy(by_id["fs-id1165133394710"])
past_boundary = False
for child in list(section):
    if child.tag == f"{{{CN}}}section":
        past_boundary = True
    if past_boundary:
        section.remove(child)
content.append(section)
for identity in ("fs-id1165137432993", "fs-id1165137870912", "fs-id1165133324915", "fs-id1165135245507", "fs-id1165135381342"):
    content.append(deepcopy(by_id[identity]))
destination = ROOT / "vi-Latn-VN/sources/m49301-pilot-source.cnxml"
destination.parent.mkdir(parents=True, exist_ok=True)
ET.indent(out)
ET.ElementTree(out).write(destination, encoding="utf-8", xml_declaration=True)
print(destination.relative_to(ROOT))
