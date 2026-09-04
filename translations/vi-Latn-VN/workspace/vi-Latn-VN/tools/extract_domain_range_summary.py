"""Print only m49304 Key Concepts; never write workspace files.

The outer Section Exercises heading is excluded and belongs to future U024.
Source identities are module-local; SECTION alone is not a global key.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MODULE = "m49304"
SECTION = "fs-id1165134077347"
LIST = "fs-id1165137591772"
PREVIOUS = "fs-id1165135440477"
STOP = "fs-id1165135176628"
ORIGINALS = (
    ("downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)


def extract(path):
    original = path.read_text(encoding="utf-8")
    document = ET.fromstring(original)
    siblings = list(document.find(CN + "content"))
    positions = [i for i, node in enumerate(siblings) if node.get("id") == SECTION]
    assert len(positions) == 1, "unique Key Concepts section"
    position = positions[0]
    assert siblings[position - 1].get("id") == PREVIOUS
    assert siblings[position + 1].get("id") == STOP
    section = siblings[position]
    assert section.get("class") == "key-concepts"
    assert [node.tag for node in section] == [CN + "title", CN + "list"]
    assert section[-1].get("id") == LIST and len(section[-1]) == 8
    assert [n.get("id") for n in section.iter() if n.get("id")] == [SECTION, LIST]
    assert [n.get("target-id") for n in section.iter(CN + "link")] == [
        f"Example_01_02_{number:02d}" for number in range(1, 14)]
    start_marker = f'<section id="{SECTION}" class="key-concepts">'
    stop_marker = f'<section id="{STOP}"'
    assert original.count(start_marker) == original.count(stop_marker) == 1
    start = original.index(start_marker)
    stop = original.index(stop_marker, start)
    body = original[start:stop].rstrip()
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n' + body + '\n</content>\n</document>\n')
    excerpt = ET.fromstring(result)
    assert len(list(excerpt.iter(CN + "section"))) == 1
    assert not list(excerpt.iter(CN + "exercise"))
    assert not list(excerpt.iter("{http://www.w3.org/1998/Math/MathML}math"))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / ORIGINALS[0][0])
    sys.stdout.reconfigure(encoding="utf-8")
    print(extract(parser.parse_args().source), end="")
