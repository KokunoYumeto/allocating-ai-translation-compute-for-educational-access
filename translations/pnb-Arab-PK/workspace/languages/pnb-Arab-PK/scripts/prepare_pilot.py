"""Materialize a bounded translation input, not a training corpus."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
NS = {"c": "http://cnx.rice.edu/cnxml", "m": "http://www.w3.org/1998/Math/MathML"}
ET.register_namespace("", NS["c"])
ET.register_namespace("m", NS["m"])
source = ROOT / "downloads/m49301.cnxml"
doc = ET.parse(source).getroot()
content = doc.find("c:content", NS)
excerpt = ET.Element("{" + NS["c"] + "}document", {"id": "m49301-pilot-excerpt"})
excerpt.append(copy.deepcopy(content[0]))
section = copy.deepcopy(content[1])
for child in list(section):
    if child.tag == "{" + NS["c"] + "}example":
        break
else:
    raise ValueError("Expected example boundary")
boundary = list(section).index(child)
for child in list(section)[boundary:]:
    section.remove(child)
excerpt.append(section)
dest = BASE / "source-excerpts"
dest.mkdir(parents=True, exist_ok=True)
ET.ElementTree(excerpt).write(dest / "m49301-opening.cnxml", encoding="utf-8", xml_declaration=True)
(BASE / "assets").mkdir(exist_ok=True)
shutil.copyfile(ROOT / "downloads/Figure_01_01_001.jpg", BASE / "assets/Figure_01_01_001.jpg")
manifest = {
    "purpose": "bounded source witness for translation; not model training or fine-tuning",
    "upstream_url": "https://github.com/openstax/osbooks-college-algebra-bundle",
    "commit": "789b54099106b071d1d32bfcee454fed72eb4768",
    "module": "m49301", "path": "modules/m49301/index.cnxml",
    "full_module_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "selection": "content opening paragraph, then section fs-id1165133394710 through how-to fs-id1165137445319 inclusive",
    "next_source_id": "Example_01_01_01",
    "excerpt_sha256": hashlib.sha256((dest / "m49301-opening.cnxml").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
    "image": {"path": "media/CNX_Precalc_Figure_01_01_001.jpg", "sha256": hashlib.sha256((BASE / "assets/Figure_01_01_001.jpg").read_bytes()).hexdigest(), "treatment": "unaltered English diagram with translated caption and bilingual legend"},
}
(dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
