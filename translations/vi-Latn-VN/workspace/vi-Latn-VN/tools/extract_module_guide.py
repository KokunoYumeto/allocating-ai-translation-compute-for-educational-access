"""Print m49301 metadata objectives and the outer exercise heading only.

The exercise section body is deliberately excluded: U009–U016 own its children.
The title and complete metadata are retained; extraction changes formatting only.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
MD = "http://cnx.rice.edu/mdml"
SECTION = "fs-id1165137737761"


def extract(path):
    original = ET.parse(path).getroot()
    metadata = original.find(f"{{{CN}}}metadata")
    abstract = metadata.find(f"{{{MD}}}abstract")
    assert [node.get("id") for node in abstract] == ["para-00001", "list-00001"]
    assert len(abstract.find(f"{{{CN}}}list")) == 5
    assert metadata.find(f"{{{MD}}}content-id").text == "m49301"
    section = original.find(f".//{{{CN}}}section[@id='{SECTION}']")
    assert section.get("class") == "section-exercises"
    assert list(section)[0].tag == f"{{{CN}}}title"
    assert list(section)[1].get("id") == "fs-id1165137432988"
    result = ET.Element(f"{{{CN}}}document", {
        "source-module": "m49301",
        "scope": "metadata-and-section-exercises-heading-only",
    })
    result.append(deepcopy(original.find(f"{{{CN}}}title")))
    result.append(deepcopy(metadata))
    content = ET.SubElement(result, f"{{{CN}}}content")
    heading = ET.SubElement(content, section.tag, dict(section.attrib))
    heading.append(deepcopy(section.find(f"{{{CN}}}title")))
    for node in result.iter():
        if node.text and node.text.isspace():
            node.text = None
        if node.tail and node.tail.isspace():
            node.tail = None
    ET.register_namespace("", CN)
    ET.register_namespace("md", MD)
    ET.indent(result, space="  ")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(result, encoding="unicode") + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    print(extract(parser.parse_args().source), end="")
