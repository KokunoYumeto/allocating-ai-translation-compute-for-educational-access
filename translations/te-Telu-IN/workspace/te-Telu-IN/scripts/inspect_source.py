"""Bounded source inspection for this translation project (not a training export)."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"


def section():
    path = ROOT / "downloads/upstream-prealgebra/modules/m81243/index.cnxml"
    if not path.exists():
        path = ROOT / "downloads/openstax-prealgebra-2e-id-ID/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml"
    root = ET.parse(path).getroot()
    return next(e for e in root.iter() if e.get("id") == "fs-id1830385")


def slots(root):
    """All nonblank prose/accessibility slots; MathML tokens stay unchanged."""
    for element in root.iter():
        for key in ("text", "tail", "alt", "aria-label", "summary"):
            value = element.get(key) if key in ("alt", "aria-label", "summary") else getattr(element, key)
            if value and value.strip():
                yield element, key, value


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for i, (element, key, value) in enumerate(slots(section()), 1):
        print(f"s{i:03d} {element.tag.split('}')[-1]} {key}: {value}")
