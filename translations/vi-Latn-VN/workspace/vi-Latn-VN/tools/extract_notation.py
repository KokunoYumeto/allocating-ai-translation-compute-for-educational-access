"""Extract the complete next subsection and its one admitted original figure."""
from copy import deepcopy
import csv
from hashlib import sha256
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "vi-Latn-VN"
CN = "http://cnx.rice.edu/cnxml"
ET.register_namespace("", CN)
ET.register_namespace("m", "http://www.w3.org/1998/Math/MathML")
ET.register_namespace("md", "http://cnx.rice.edu/mdml")
source = ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml"
tree = ET.parse(source)
section = next(e for e in tree.iter() if e.get("id") == "fs-id1165134474160")
out = ET.Element(f"{{{CN}}}document", {"source-module": "m49301", "scope": "complete-notation-subsection"})
ET.SubElement(out, f"{{{CN}}}title").text = "Using Function Notation"
ET.SubElement(out, f"{{{CN}}}content").append(deepcopy(section))
ET.indent(out)
ET.ElementTree(out).write(LANG / "sources/m49301-notation-source.cnxml", encoding="utf-8", xml_declaration=True)
filename = "CNX_Precalc_Figure_01_01_005.jpg"
asset = ROOT / "downloads/upstream-openstax/media" / filename
with (ROOT / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv").open(encoding="utf-8-sig", newline="") as stream:
    rows = [r for r in csv.DictReader(stream) if Path(r["asset_path"]).name == filename]
assert len(rows) == 1 and rows[0]["admission"] == "admitted"
assert sha256(asset.read_bytes()).hexdigest() == rows[0]["sha256"]
shutil.copyfile(asset, LANG / "assets" / filename)
(LANG / "provenance/notation-asset-notice.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"section": section.get("id"), "source_ids": sum(bool(e.get("id")) for e in section.iter()), "asset_bytes": asset.stat().st_size, "asset_sha256": rows[0]["sha256"]}))
