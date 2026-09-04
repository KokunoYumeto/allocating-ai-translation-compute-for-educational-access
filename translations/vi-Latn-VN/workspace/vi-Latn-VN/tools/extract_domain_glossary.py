"""Print the complete final m49304 glossary, preserving its raw inner XML."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
DEFINITIONS = ["fs-id1165135445751", "fs-id1165135487256", "fs-id1165137863188"]


def extract(path):
    original = path.read_text(encoding="utf-8")
    document = ET.fromstring(original)
    children = list(document)
    glossary = document.find(CN+"glossary")
    assert glossary is not None and children[-1] is glossary
    assert children[-2].tag == CN+"content"
    assert children[-2][-1].get("id") == "fs-id1165135176628"
    assert children[-2][-1][-1].get("id") == "fs-id1165137832031"
    assert [n.get("id") for n in glossary] == DEFINITIONS
    assert all(n.tag == CN+"definition" for n in glossary)
    assert original.count("<glossary>") == original.count("</glossary>") == 1
    inner = original.split("<glossary>",1)[1].split("</glossary>",1)[0]
    result = ('<glossary xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">'+inner+'</glossary>\n')
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 6
    assert len(list(excerpt.iter(M+"math"))) == 1
    assert len(list(excerpt.iter(M+"mtext"))) == 1
    assert len(list(excerpt.iter(CN+"meaning"))) == 3
    assert not list(excerpt.iter(CN+"exercise")) and not list(excerpt.iter(CN+"image"))
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,
                        default=ROOT.parent/"downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source),end="")
