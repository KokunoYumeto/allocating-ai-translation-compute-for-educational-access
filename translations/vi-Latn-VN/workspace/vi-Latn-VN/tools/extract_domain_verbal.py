"""Print m49304 Section Exercises heading plus the complete Verbal category."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
OUTER = "fs-id1165135176628"
SECTION = "fs-id1165135172218"
STOP = "fs-id1165137771069"
EXERCISES = ["fs-id1165137665109", "fs-id1165135440209", "fs-id1165137635386",
             "fs-id1165134042454", "fs-id1165134211324"]


def extract(path):
    original = path.read_text(encoding="utf-8")
    root = ET.fromstring(original)
    outer = root.find(f".//*[@id='{OUTER}']")
    children = list(outer)
    assert children[0].tag == CN + "title"
    assert children[1].get("id") == SECTION
    assert children[2].get("id") == STOP
    section = children[1]
    assert [n.get("id") for n in section.iter(CN + "exercise")] == EXERCISES
    start = f'<section id="{OUTER}" class="section-exercises">'
    stop = f'<section id="{STOP}">'
    assert original.count(start) == original.count(stop) == 1
    body = original[original.index(start):original.index(stop)].rstrip()
    result = (
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
        f"<content>\n{body}\n</section>\n</content>\n</document>\n"
    )
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 23
    assert len(list(excerpt.iter(M + "math"))) == 12
    assert len(list(excerpt.iter(CN + "exercise"))) == 5
    assert len(list(excerpt.iter(CN + "solution"))) == 3
    assert len(list(excerpt.iter(CN + "image"))) == 0
    assert len(list(excerpt.iter(M + "mtext"))) == 0
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
