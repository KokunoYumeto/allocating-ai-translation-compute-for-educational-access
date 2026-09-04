"""Print the complete m49304 piecewise-functions section without file writes."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165135440477"
STOP = "fs-id1165134077347"


def extract(path):
    original = path.read_text(encoding="utf-8")
    root = ET.fromstring(original)
    children = list(root.find(CN + "content"))
    index = next(i for i, node in enumerate(children) if node.get("id") == SECTION)
    section = children[index]
    assert children[index + 1].get("id") == STOP
    assert children[index + 1].get("class") == "key-concepts"
    assert section[-1].get("id") == "fs-id1165135190393"
    assert [n.get("id") for n in section.iter(CN + "example")] == [
        "Example_01_02_11", "Example_01_02_12", "Example_01_02_13"]
    assert [n.get("id") for n in section.iter(CN + "exercise")] == [
        "fs-id1165137452506", "fs-id1165135436662", "fs-id1165137781618", "ti_01_02_06"]
    start = f'<section id="{SECTION}">'
    stop = f'<section id="{STOP}" class="key-concepts">'
    assert original.count(start) == original.count(stop) == 1
    body = original[original.index(start):original.index(stop)].rstrip()
    result = (
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
        f'<title>{section.find(CN + "title").text}</title>\n'
        f"<content>\n{body}\n</content>\n</document>\n"
    )
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 78
    assert len(list(excerpt.iter(M + "math"))) == 38
    assert len(list(excerpt.iter(CN + "image"))) == 5
    assert len(list(excerpt.iter(CN + "solution"))) == 4
    assert len([n for n in section[-1].iter(CN + "link") if n.get("url")]) == 5
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
