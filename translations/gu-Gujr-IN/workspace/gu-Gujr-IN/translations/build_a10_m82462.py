"""Build the complete source-bound Gujarati translation of A10 m82462."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82462/index.cnxml"
MAP = Path(__file__).with_name("a10-m82462.slots.json")
TSV = Path(__file__).with_name("a10-m82462.gu.tsv")
OUT = Path(__file__).with_name("a10-m82462.gu.cnxml")
SOURCE_SHA256 = "7f29e8b9558d6d37553e5991cfffc7cc27c320e2a92ed98db563e76a90e8a51e"
CNX = "http://cnx.rice.edu/cnxml"
MD = "http://cnx.rice.edu/mdml"


def prose_slots(root):
    for elem in root.iter():
        local = elem.tag.rsplit("}", 1)[-1]
        if local in {"content-id", "uuid"}:
            continue
        if elem.text and re.search(r"[A-Za-z]", elem.text):
            yield elem, "text", elem.text.strip()
        if elem.tail and re.search(r"[A-Za-z]", elem.tail):
            yield elem, "tail", elem.tail.strip()
        for attr in ("alt", "aria-label", "summary", "title"):
            value = elem.get(attr)
            if value and re.search(r"[A-Za-z]", value):
                yield elem, "@" + attr, value.strip()


def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest() == SOURCE_SHA256
    tree = ET.parse(SRC)
    root = tree.getroot()
    unique = list(dict.fromkeys(value for _, _, value in prose_slots(root)))
    mapping = json.loads(MAP.read_text(encoding="utf-8"))
    assert mapping["source_sha256"] == SOURCE_SHA256
    assert [row["en"] for row in mapping["slots"]] == unique
    authored = {}
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        number, gu = line.split("\t", 1)
        number = int(number)
        assert number not in authored
        authored[number] = gu
    assert set(authored) == set(range(len(unique)))
    translated = {row["en"]: authored[row["n"]] for row in mapping["slots"]}
    for elem, attr, source in prose_slots(root):
        gu = translated[source]
        if attr.startswith("@"):
            elem.set(attr[1:], gu)
        else:
            old = getattr(elem, attr)
            setattr(elem, attr, old[: len(old) - len(old.lstrip())] + gu + old[len(old.rstrip()) :])
    root.set("{http://www.w3.org/XML/1998/namespace}lang", "gu-Gujr-IN")
    ET.register_namespace("", CNX)
    ET.register_namespace("md", MD)
    tree.write(OUT, encoding="utf-8", xml_declaration=True)
    print(f"Translated {len(unique)} slots")


if __name__ == "__main__":
    main()
