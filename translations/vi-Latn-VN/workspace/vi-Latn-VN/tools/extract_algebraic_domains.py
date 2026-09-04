"""Print complete m49304 Algebraic exercises6–26; no filesystem writes."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
MODULE = "m49304"
PARENT = "fs-id1165135176628"
SECTION = "fs-id1165137771069"
PROMPT = "fs-id1165137408926"
PREVIOUS = "fs-id1165135172218"
STOP = "fs-id1165137580833"
EXERCISES = (
    "fs-id1165137833819", "fs-id1165137854912", "fs-id1165135512534",
    "fs-id1165137473385", "fs-id1165135192268", "fs-id1165137629066",
    "fs-id1165137807107", "fs-id1165134259277", "fs-id1165135503751",
    "fs-id1165133276237", "fs-id1165137810520", "fs-id1165135548992",
    "fs-id1165135593402", "fs-id1165135191342", "fs-id1165137921795",
    "fs-id1165137476914", "fs-id1165135185292", "fs-id1165135252252",
    "fs-id1165137601712", "fs-id1165137628472", "fs-id1165137469452",
)
ORIGINALS = (
    ("downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)


def extract(path):
    original = path.read_text(encoding="utf-8")
    document = ET.fromstring(original)
    parent = next(n for n in document.iter() if n.get("id") == PARENT)
    siblings = list(parent)
    index = next(i for i, n in enumerate(siblings) if n.get("id") == SECTION)
    assert siblings[index - 1].get("id") == PREVIOUS
    assert siblings[index + 1].get("id") == STOP
    section = siblings[index]
    assert section[0].tag == CN + "title" and section[1].get("id") == PROMPT
    assert [n.get("id") for n in section.iter(CN + "exercise")] == list(EXERCISES)
    assert section[-1].get("id") == EXERCISES[-1]
    assert section[-1][-1][-1].get("id") == "fs-id1165137938832"
    start_marker, stop_marker = f'<section id="{SECTION}">', f'<section id="{STOP}">'
    assert original.count(start_marker) == original.count(stop_marker) == 1
    body = original[original.index(start_marker):original.index(stop_marker)].rstrip()
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n' + body + '\n</content>\n</document>\n')
    excerpt = ET.fromstring(result)
    assert len([n for n in excerpt.iter() if n.get("id")]) == 86
    assert len(list(excerpt.iter(M + "math"))) == 31
    assert len(list(excerpt.iter(CN + "solution"))) == 10
    assert not list(excerpt.iter(CN + "image"))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / ORIGINALS[0][0])
    sys.stdout.reconfigure(encoding="utf-8")
    print(extract(parser.parse_args().source), end="")
