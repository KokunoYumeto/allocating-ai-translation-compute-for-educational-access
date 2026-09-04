"""Print stable read-only translation slots for one frozen CNXML block."""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

import build


def qname(tag):
    namespace, local = tag[1:].split("}", 1)
    prefix = {build.C: "c", build.M: "m", build.D: "md"}.get(namespace)
    assert prefix, tag
    return f"{prefix}:{local}"


def child_path(parent_path, parent, child):
    same = [candidate for candidate in parent if candidate.tag == child.tag]
    index = same.index(child) + 1
    suffix = f"[{index}]" if len(same) > 1 else ""
    return f"{parent_path}/{qname(child.tag)}{suffix}"


def inventory(root):
    records = []

    def visit(element, path):
        if element.tag.startswith(f"{{{build.M}}}"):
            if build.local(element) == "mtext" and re.search(r"[A-Za-z]{2,}", element.text or ""):
                records.append({"kind": "math_text", "xpath": path, "source": element.text})
            for child in element:
                visit(child, child_path(path, element, child))
            return

        slots = [element.text or ""] + [child.tail or "" for child in element]
        if any(slot.strip() for slot in slots):
            records.append({
                "kind": "slots",
                "tag": build.local(element),
                "id": element.get("id"),
                "xpath": path,
                "slots": slots,
            })
        for attribute in ("alt", "aria-label", "summary"):
            if attribute in element.attrib:
                records.append({
                    "kind": attribute,
                    "tag": build.local(element),
                    "id": element.get("id"),
                    "xpath": path,
                    "source": element.get(attribute),
                })
        for child in element:
            visit(child, child_path(path, element, child))

    visit(root, ".")
    return records


def main():
    assert len(sys.argv) == 3, "usage: inventory_slots.py MODULE SECTION_ID"
    module, section = sys.argv[1:]
    document = ET.parse(build.module_source(module))
    root = document.find(f'.//*[@id="{section}"]')
    assert root is not None, section
    print(json.dumps(inventory(root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
