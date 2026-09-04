"""Print the complete, final m49301 glossary; never write workspace files."""
from copy import deepcopy
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
ORIGINALS = (
    ("downloads/upstream-openstax/modules/m49301/index.cnxml",
     "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612"),
    ("downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml",
     "67678da7d3faa988d0c42a63ef15f140a2c0478610cd1fadc499fb749d55c77a"),
)
DEFINITION_IDS = (
    "fs-id1165137758543", "fs-id1165137758552", "fs-id1165137932580",
    "fs-id1165137932588", "fs-id1165134149782", "fs-id1165135511353",
    "fs-id1165135511364", "fs-id1165135508564", "fs-id1165135508573",
    "fs-id1165135315533", "fs-id1165135315542",
)


def selected(path):
    document = ET.parse(path).getroot()
    children = list(document)
    glossary = document.find(f"{{{CN}}}glossary")
    assert glossary is not None and children[-1] is glossary, "glossary is final direct child"
    assert children[-2].tag == f"{{{CN}}}content", "glossary follows complete content"
    end_exercises = children[-2][-1]
    assert end_exercises.get("id") == "fs-id1165137737761"
    assert end_exercises[-1].get("id") == "fs-id1165135580349"
    assert [node.get("id") for node in glossary] == list(DEFINITION_IDS)
    assert all(node.tag == f"{{{CN}}}definition" for node in glossary)
    result = deepcopy(glossary)
    for node in result.iter():
        if node.text and node.text.isspace():
            node.text = None
        if node.tail and node.tail.isspace():
            node.tail = None
    result.tail = None
    return result


def extract(path):
    ET.register_namespace("", CN)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(
        selected(path), encoding="unicode", short_empty_elements=True
    ) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / ORIGINALS[0][0])
    arguments = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    print(extract(arguments.source), end="")
