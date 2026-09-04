"""Extract the complete m49304 toolkit domain/range section.

Default: print UTF-8 XML without writing. --write saves only this unit's owned
excerpt through safe_output.write_atomic. No source file is edited or fetched.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165134384565"
STOP = "fs-id1165135440477"
OUTPUT = ROOT / "sources/m49304-toolkit-domains-ranges-source.cnxml"


def extract(path):
    original = Path(path).read_text(encoding="utf-8")
    document = ET.fromstring(original)
    content = document.find(CN + "content")
    siblings = list(content)
    positions = [i for i, node in enumerate(siblings) if node.get("id") == SECTION]
    assert len(positions) == 1, "unique selected section"
    position = positions[0]
    assert siblings[position - 1].get("id") == "fs-id1165137653855"
    assert siblings[position + 1].get("id") == STOP
    section = siblings[position]
    assert section[-1].get("id") == "fs-id1165137430800"
    assert section[-1].find(CN + "exercise").get("id") == "ti_01_02_05"
    assert [node.get("id") for node in section.iter(CN + "example")] == [
        "Example_01_02_08", "Example_01_02_09", "Example_01_02_10"]
    assert [node.get("id") for node in section.iter(CN + "figure")] == [
        f"Figure_01_02_{number:03d}" for number in range(11, 21)]
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
    assert len([node for node in excerpt.iter() if node.get("id")]) == 55
    assert len(list(excerpt.iter(M + "math"))) == 41
    assert len(list(excerpt.iter(CN + "image"))) == 10
    assert len(list(excerpt.iter(CN + "caption"))) == 9
    assert len(list(excerpt.iter(CN + "exercise"))) == 4
    assert len(list(excerpt.iter(CN + "solution"))) == 4
    assert not list(excerpt.iter(CN + "table"))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    text = extract(arguments.source)
    if arguments.write:
        from safe_output import write_atomic
        write_atomic(OUTPUT, text.encode("utf-8"))
        print(OUTPUT)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text, end="")
