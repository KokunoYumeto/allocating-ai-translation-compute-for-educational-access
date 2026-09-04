"""Extract the first complete m49304 Graphical exercise block, #27–37.

Keep the Graphical parent/title and first shared prompt. Stop before the next
shared prompt, which introduces piecewise-function sketches. Print by default;
--write saves only this unit's owned excerpt through safe_output.write_atomic.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137580833"
PROMPT = "fs-id1165135186809"
STOP = "fs-id1165137785119"
EXERCISES = [
    "fs-id1165135168172", "fs-id1165135160181", "fs-id1165137723404",
    "fs-id1165137590678", "fs-id1165137737326", "fs-id1165137404973",
    "fs-id1165137544188", "fs-id1165135176309", "fs-id1165137642580",
    "fs-id1165137442385", "fs-id1165137851981",
]
OUTPUT = ROOT / "sources/m49304-domain-range-exercises-source.cnxml"


def extract(path):
    original = Path(path).read_text(encoding="utf-8")
    document = ET.fromstring(original)
    outer = document.find(f".//{CN}section[@id='fs-id1165135176628']")
    section = outer.find(f"{CN}section[@id='{SECTION}']")
    siblings = list(outer)
    assert siblings[siblings.index(section) - 1].get("id") == "fs-id1165137771069"
    assert siblings[siblings.index(section) + 1].get("id") == "fs-id1165134118450"
    children = list(section)
    positions = [i for i, node in enumerate(children) if node.get("id") == STOP]
    assert positions == [13], "exact second shared prompt boundary"
    selected = children[:positions[0]]
    assert selected[0].tag == CN + "title" and selected[1].get("id") == PROMPT
    assert [node.get("id") for node in selected[2:]] == EXERCISES
    assert children[14].get("id") == "fs-id1165137462167"
    all_exercises = list(outer.iter(CN + "exercise"))
    assert [all_exercises.index(node) + 1 for node in selected[2:]] == list(range(27, 38))
    start_marker = f'<section id="{SECTION}">'
    stop_marker = f'<para id="{STOP}">'
    assert original.count(start_marker) == original.count(stop_marker) == 1
    start = original.index(start_marker)
    stop = original.index(stop_marker, start)
    body = original[start:stop].rstrip()
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n' + body + '\n</section>\n</content>\n</document>\n')
    excerpt = ET.fromstring(result)
    assert len([node for node in excerpt.iter() if node.get("id")]) == 47
    assert len(list(excerpt.iter(M + "math"))) == 12
    assert len(list(excerpt.iter(CN + "image"))) == 11
    assert len(list(excerpt.iter(CN + "exercise"))) == 11
    assert len(list(excerpt.iter(CN + "solution"))) == 6
    assert not list(excerpt.iter(CN + "figure"))
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
