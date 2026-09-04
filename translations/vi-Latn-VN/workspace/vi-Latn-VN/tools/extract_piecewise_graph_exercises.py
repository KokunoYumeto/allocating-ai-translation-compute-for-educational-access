"""Print the second m49304 Graphical exercise slice, without file writes."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
PARENT = "fs-id1165137580833"
FIRST = "fs-id1165137785119"
STOP = "fs-id1165134118450"
EXERCISES = ["fs-id1165137462167", "fs-id1165137562309", "fs-id1165137628033",
             "fs-id1165135641679", "fs-id1165135192719", "fs-id1165137594981",
             "fs-id1165137571389", "fs-id1165137407891"]


def extract(path):
    original = path.read_text(encoding="utf-8")
    root = ET.fromstring(original)
    outer = root.find(".//*[@id='fs-id1165135176628']")
    siblings = list(outer)
    parent = root.find(f".//*[@id='{PARENT}']")
    assert siblings[siblings.index(parent) + 1].get("id") == STOP
    children = list(parent)
    index = next(i for i, node in enumerate(children) if node.get("id") == FIRST)
    selected = children[index:]
    assert [n.get("id") for n in selected[1:]] == EXERCISES
    assert all(n.tag == CN + "exercise" for n in selected[1:])
    start, stop = f'<para id="{FIRST}">', f'<section id="{STOP}">'
    assert original.count(start) == original.count(stop) == 1
    body = original[original.index(start):original.index(stop)].rstrip()
    #body includes the original Graphical closing tag; an anonymous wrapper
    #replaces its excluded opening/title, without duplicating the parent's ID.
    result = (
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
        f"<content>\n<section>\n{body}\n</content>\n</document>\n"
    )
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 37
    assert len(list(excerpt.iter(M + "math"))) == 12
    assert len(list(excerpt.iter(CN + "solution"))) == 4
    assert len(list(excerpt.iter(CN + "image"))) == 4
    assert len(list(excerpt.iter(M + "mtext"))) == 16
    assert all(n.get("id") != PARENT for n in excerpt.iter())
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml")
    print(extract(parser.parse_args().source), end="")
