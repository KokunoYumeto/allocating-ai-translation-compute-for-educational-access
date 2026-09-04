"""Print the complete Technology section of pinned m49301 to stdout."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
SECTION = "fs-id1165134373511"
STOP = "fs-id1165135580349"
PROMPTS = ("fs-id1165135530586", "fs-id1165135388446", "fs-id1165135634160", "fs-id1165137539207")
EXERCISE_IDS = (
    "fs-id1165135530591",
    "fs-id1165134087674",
    "fs-id1165135695182",
    "fs-id1165134060421",
    "fs-id1165133195224",
    "fs-id1165133402070",
    "fs-id1165137844302",
    "fs-id1165137540730",
    "fs-id1165137605840",
    "fs-id1165134031227",
    "fs-id1165134087649",
    "fs-id1165135251229",
)


def extract(path):
    raw = Path(path).read_text(encoding="utf-8")
    original = ET.fromstring(raw)
    section = original.find(f".//{CN}section[@id='{SECTION}']")
    assert [n.get("id") for n in section if n.tag == CN + "exercise"] == list(EXERCISE_IDS)
    assert [n.get("id") for n in section if n.tag == CN + "para"] == list(PROMPTS)
    parent = next(n for n in original.iter() if section in list(n))
    assert list(parent)[list(parent).index(section) + 1].get("id") == STOP
    start = raw.index(f'<section id="{SECTION}"')
    finish = raw.index("</section>", start) + len("</section>")
    content = raw[start:finish]
    result = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" '
        'source-module="m49301" scope="complete-technology-exercises">\n'
        "  <title>Technology: Graphs on Closed Domains</title>\n  <content>\n"
        + content + "\n  </content>\n</document>\n"
    )
    assert len(list(ET.fromstring(result).iter(CN + "exercise"))) == 12
    return result


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml")
    print(extract(parser.parse_args().source), end="")
