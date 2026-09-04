"""Print complete m49304 Technology: exercises55–56, without file writes."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
OUTER = "fs-id1165135176628"
SECTION = "fs-id1165135194497"
PREVIOUS = "fs-id1165134118450"
STOP = "fs-id1165137733672"
EXERCISES = ["fs-id1165137780865", "fs-id1165131911953"]


def extract(path):
    original = path.read_text(encoding="utf-8")
    root = ET.fromstring(original)
    outer = root.find(f".//*[@id='{OUTER}']")
    children = list(outer)
    index = next(i for i, n in enumerate(children) if n.get("id") == SECTION)
    assert children[index - 1].get("id") == PREVIOUS
    assert children[index + 1].get("id") == STOP
    section = children[index]
    assert [n.get("id") for n in section.iter(CN + "exercise")] == EXERCISES
    start, stop = f'<section id="{SECTION}">', f'<section id="{STOP}">'
    assert original.count(start) == original.count(stop) == 1
    body = original[original.index(start):original.index(stop)].rstrip()
    result = (
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
        f"<content>\n{body}\n</content>\n</document>\n"
    )
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 12
    assert len(list(excerpt.iter(M + "math"))) == 10
    assert len(list(excerpt.iter(CN + "solution"))) == 1
    assert len(list(excerpt.iter(CN + "image"))) == 2
    assert len(list(excerpt.iter(M + "mtext"))) == 0
    assert OUTER not in [n.get("id") for n in excerpt.iter()]
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
