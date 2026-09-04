"""Print the complete m49304 notation section without file writes."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137677916"
STOP = "fs-id1165137653855"


def extract(path):
    original = path.read_text(encoding="utf-8")
    parsed = ET.fromstring(original)
    content = parsed.find(CN + "content")
    children = list(content)
    position = next(i for i, n in enumerate(children) if n.get("id") == SECTION)
    section = children[position]
    assert children[position + 1].get("id") == STOP
    assert section[-1].get("id") == "fs-id1165137779165"
    assert [n.get("id") for n in section.iter(CN + "example")] == ["Example_01_02_05"]
    assert [n.get("id") for n in section.iter(CN + "exercise")] == [
        "fs-id1165134342702", "ti_01_02_03"]
    start_marker = f'<section id="{SECTION}">'
    stop_marker = f'<section id="{STOP}">'
    assert original.count(start_marker) == original.count(stop_marker) == 1
    body = original[original.index(start_marker):original.index(stop_marker)].rstrip()
    title = section.find(CN + "title").text
    result = (
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
        f"<title>{title}</title>\n<content>\n{body}\n</content>\n</document>\n"
    )
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 36
    assert len(list(excerpt.iter(M + "math"))) == 24
    assert len(list(excerpt.iter(CN + "image"))) == 3
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
