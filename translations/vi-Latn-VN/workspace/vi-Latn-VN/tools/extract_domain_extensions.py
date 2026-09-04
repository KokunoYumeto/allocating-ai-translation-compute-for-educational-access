"""Extract the complete pinned m49304 Extensions section, exercises57–59.

Print by default. Explicit --write saves only the fixed owned excerpt through
safe_output.write_atomic. Originals are existing local inputs, never fetched.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137733672"
STOP = "fs-id1165137832031"
EXERCISES = ["fs-id1165137442197", "fs-id1165137679047", "fs-id1165135209378"]
OUTPUT = ROOT / "sources/m49304-domain-extensions-source.cnxml"


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def extract(path):
    original = Path(path).read_text(encoding="utf-8")
    document = ET.fromstring(original)
    outer = document.find(f".//{CN}section[@id='fs-id1165135176628']")
    section = outer.find(f"{CN}section[@id='{SECTION}']")
    siblings = list(outer)
    position = siblings.index(section)
    assert siblings[position - 1].get("id") == "fs-id1165135194497"
    assert siblings[position + 1].get("id") == STOP
    assert len(list(section.iter(CN + "section"))) == 1
    exercises = list(section.iter(CN + "exercise"))
    assert [node.get("id") for node in exercises] == EXERCISES
    all_exercises = list(outer.iter(CN + "exercise"))
    assert [all_exercises.index(node) + 1 for node in exercises] == [57, 58, 59]
    assert [node.get("id") for node in section.iter(CN + "solution")] == [
        "fs-id1165134555582", "fs-id1165133210812"]
    marker = f'<section id="{SECTION}">'
    assert original.count(marker) == 1
    start = original.index(marker)
    end = original.index("</section>", start) + len("</section>")
    assert end < original.index(f'<section id="{STOP}">', start)
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n' + original[start:end] + '\n</content>\n</document>\n')
    excerpt = ET.fromstring(result)
    assert canonical(excerpt.find(CN + "content/" + CN + "section")) == canonical(section)
    assert len([node for node in excerpt.iter() if node.get("id")]) == 14
    assert len(list(excerpt.iter(M + "math"))) == 6
    assert not list(excerpt.iter(CN + "image"))
    assert not list(excerpt.iter(CN + "table"))
    assert not list(excerpt.iter(CN + "link"))
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
