"""Print the exact first two Algebraic exercise blocks from pinned m49301.

Stdout is the small CNXML excerpt; it never downloads or edits source files.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
PARENT = "fs-id1165134080937"
START_PROMPT = "fs-id1165134080942"
SECOND_PROMPT = "fs-id1165135318984"
STOP = "fs-id1165134066606"
EXERCISE_IDS = (
    "fs-id1165134080945", "fs-id1165135570225", "fs-id1165137841682",
    "fs-id1165137925514", "fs-id1165137942483", "fs-id1165135394228",
    "fs-id1165135675195", "fs-id1165137864148", "fs-id1165137679356",
    "fs-id1165137661060", "fs-id1165135581214", "fs-id1165133202429",
    "fs-id1165134042772", "fs-id1165137887434", "fs-id1165137658561",
    "fs-id1165137777686", "fs-id1165137892513", "fs-id1165134216874",
    "fs-id1165135538770", "fs-id1165135203596", "fs-id1165137599984",
)


def extract(source_path):
    raw = Path(source_path).read_text(encoding="utf-8")
    original = ET.fromstring(raw)
    parent = original.find(f".//{CN}section[@id='{PARENT}']")
    selected = []
    for node in parent:
        if node.get("id") == STOP:
            break
        selected.append(node)
    assert [node.get("id") for node in selected if node.tag == CN + "exercise"] == list(EXERCISE_IDS)
    assert [node.get("id") for node in selected if node.tag == CN + "para"] == [START_PROMPT, SECOND_PROMPT]
    start = raw.index(f'<section id="{PARENT}"')
    stop = raw.index(f'<para id="{STOP}"', start)
    section = raw[start:stop].rstrip() + "\n</section>"
    result = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" '
        'source-module="m49301" scope="algebraic-classification-first-21-exercises">\n'
        "  <title>Algebraic: Function Classification</title>\n  <content>\n"
        + section + "\n  </content>\n</document>\n"
    )
    parsed = ET.fromstring(result)
    assert len(list(parsed.iter(CN + "exercise"))) == 21
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    args = parser.parse_args()
    print(extract(args.source), end="")
