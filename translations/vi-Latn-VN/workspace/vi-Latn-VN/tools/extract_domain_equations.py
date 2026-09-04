"""Print the complete opening teaching unit of m49304, without file writes.

Retain original title/metadata, movie introduction/figure and the first complete
teaching section. Stop before the next section, Using Notations to Specify Domain
and Range. The second abstract objective remains a whole-module objective.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165135193832"
STOP = "fs-id1165137677916"


def extract(path):
    original = path.read_text(encoding="utf-8")
    parsed = ET.fromstring(original)
    content = parsed.find(CN + "content")
    assert [n.get("id") for n in list(content)[:4]] == [
        "fs-id1165137404978", "Figure_01_02_001", SECTION, STOP]
    first = content[2]
    assert first[-1].get("id") == "fs-id1165134328219"
    assert len(list(first.iter(CN + "example"))) == 4
    assert len([n for n in first.iter(CN + "note") if "try" in n.get("class", "").split()]) == 4
    marker = f'<section id="{STOP}">'
    assert original.count(marker) == 1
    result = original[:original.index(marker)].rstrip() + "\n</content>\n</document>\n"
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 97
    assert len(list(excerpt.iter(M + "math"))) == 32
    assert len(list(excerpt.iter(CN + "image"))) == 4
    assert len(excerpt.find(CN + "metadata/" + MD + "abstract/" + CN + "list")) == 2
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
