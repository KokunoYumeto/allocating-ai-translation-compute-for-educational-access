"""Extract the first15 Graphical exercises of pinned m49301 to stdout.

The old planning map named the fourteenth exercise as the endpoint. Actual
source adjacency puts exercise4325868/Figure215 before shared prompt5531627.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
PARENT = "fs-id1165135664071"
START_PROMPT = "fs-id1165135664077"
STOP = "fs-id1165135531627"
EXERCISE_IDS = (
    "fs-id1165135455987",
    "fs-id1165137527641",
    "fs-id1165135332512",
    "fs-id1165137742393",
    "fs-id1165135386379",
    "fs-id1165137749974",
    "fs-id1165137399704",
    "fs-id1165137883764",
    "fs-id1165134497159",
    "fs-id1165135496435",
    "fs-id1165137911653",
    "fs-id1165135593325",
    "fs-id1165134240968",
    "fs-id1165135632092",
    "fs-id1165134325868",
)


def extract(path):
    raw = Path(path).read_text(encoding="utf-8")
    original = ET.fromstring(raw)
    parent = original.find(f".//{CN}section[@id='{PARENT}']")
    selected = []
    for node in parent:
        if node.get("id") == STOP:
            break
        selected.append(node)
    assert [node.get("id") for node in selected if node.tag == CN + "exercise"] == list(EXERCISE_IDS)
    assert [node.get("id") for node in selected if node.tag == CN + "para"] == [START_PROMPT]
    start = raw.index(f'<section id="{PARENT}"')
    stop = raw.index(f'<para id="{STOP}"', start)
    section = raw[start:stop].rstrip() + "\n</section>"
    result = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" '
        'source-module="m49301" scope="graphical-first-15-exercises">\n'
        "  <title>Graphical: Vertical Tests and Reading Function Values</title>\n  <content>\n"
        + section + "\n  </content>\n</document>\n"
    )
    assert len(list(ET.fromstring(result).iter(CN + "exercise"))) == 15
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    print(extract(parser.parse_args().source), end="")
