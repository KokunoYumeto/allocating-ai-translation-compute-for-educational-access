"""Extract the complete Verbal category, keeping its source solutions/IDs."""
from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[2]
CN = "http://cnx.rice.edu/cnxml"
SECTION = "fs-id1165137432988"
STOP = "fs-id1165134080937"
ET.register_namespace("", CN)


def extract(path):
    root = ET.parse(path).getroot()
    parent = next(n for n in root.iter() if n.get("id") == "fs-id1165137737761")
    children = list(parent)
    index = next(i for i, n in enumerate(children) if n.get("id") == SECTION)
    assert children[index + 1].get("id") == STOP
    wrapper = ET.Element("source-excerpt", {"module": "m49301", "stop-before": STOP})
    wrapper.append(deepcopy(children[index]))
    return wrapper


def main():
    english = extract(ROOT / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    indonesian = extract(ROOT / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml")
    ids = lambda tree: [n.get("id") for n in tree.iter() if n.get("id")]
    assert ids(english) == ids(indonesian)
    assert len(list(english.iter(f"{{{CN}}}exercise"))) == 5
    assert len(list(english.iter(f"{{{CN}}}solution"))) == 3
    write_atomic(ROOT / "vi-Latn-VN/sources/m49301-verbal-exercises-source.cnxml",
                 ET.tostring(english, encoding="utf-8", xml_declaration=True))
    print(f"Extracted {len(ids(english))} IDs, 5 exercises (2 repeated from U001), 3 source solutions")


if __name__ == "__main__":
    main()
