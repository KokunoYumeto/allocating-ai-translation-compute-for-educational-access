"""Extract the complete one-to-one subsection; its referenced figure is already local."""
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
ET.register_namespace("", CN)
ET.register_namespace("m", "http://www.w3.org/1998/Math/MathML")
tree = ET.parse(ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml")
node = next(n for n in tree.iter() if n.get("id") == "fs-id1165135422920")
write_atomic(ROOT / "vi-Latn-VN/sources/m49301-one-to-one-source.cnxml", ET.tostring(node, encoding="utf-8", xml_declaration=True))
print(f"Extracted {sum(bool(n.get('id')) for n in node.iter())} source IDs")
