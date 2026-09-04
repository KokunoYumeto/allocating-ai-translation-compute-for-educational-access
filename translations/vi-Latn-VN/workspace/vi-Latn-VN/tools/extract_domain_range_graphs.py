"""Print the complete m49304 graph-reading section; never write files.

The section starts at fs-id1165137653855 and stops before its direct
sibling fs-id1165134384565. Module-local IDs are not cross-module keys.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
MODULE = "m49304"
SECTION = "fs-id1165137653855"
STOP = "fs-id1165134384565"
FINAL_NOTE = "fs-id1165137434590"


def extract(path):
    original = path.read_text(encoding="utf-8")
    document = ET.fromstring(original)
    content = document.find(CN + "content")
    siblings = list(content)
    positions = [i for i, node in enumerate(siblings) if node.get("id") == SECTION]
    assert len(positions) == 1, "unique complete teaching section"
    position = positions[0]
    assert siblings[position - 1].get("id") == "fs-id1165137677916"
    assert siblings[position + 1].get("id") == STOP
    section = siblings[position]
    assert section[-1].get("id") == FINAL_NOTE
    assert section[-1][-1].get("id") == "fs-id1165137433394"
    assert [n.get("id") for n in section.iter(CN + "example")] == [
        "Example_01_02_06", "Example_01_02_07"]
    assert len([n for n in section.iter(CN + "note")
                if "try" in n.get("class", "").split()]) == 1
    start_marker = f'<section id="{SECTION}">'
    stop_marker = f'<section id="{STOP}">'
    assert original.count(start_marker) == original.count(stop_marker) == 1
    start = original.index(start_marker)
    stop = original.index(stop_marker, start)
    body = original[start:stop].rstrip()
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n' + body + '\n</content>\n</document>\n')
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 37
    assert len(list(excerpt.iter(M + "math"))) == 13
    assert len(list(excerpt.iter(CN + "image"))) == 5
    assert len(list(excerpt.iter(CN + "exercise"))) == 3
    assert len(list(excerpt.iter(CN + "solution"))) == 3
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    sys.stdout.reconfigure(encoding="utf-8")
    print(extract(parser.parse_args().source), end="")
