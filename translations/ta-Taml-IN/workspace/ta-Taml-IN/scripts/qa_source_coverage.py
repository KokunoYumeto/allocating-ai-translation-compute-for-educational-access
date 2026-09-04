"""Report structurally checked source spans without claiming finished readers."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

LANG = Path(__file__).resolve().parents[1]
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(node):
    value = (node.text or "").strip()
    if node.tag == f"{{{M}}}mtext":
        value = re.sub(r"[^0-9$€₹.,…+\-=/×÷%]", "", value)
    return node.tag, sorted(node.attrib.items()), value, [signature(c) for c in node]


def stable_attributes(node):
    ignored = {XML_LANG}
    if node.tag == f"{{{C}}}media":
        ignored.add("alt")
    if node.tag == f"{{{C}}}image":
        ignored.update(("src", "mime-type"))
    if node.tag == f"{{{C}}}table":
        ignored.add("aria-label")
    return {k: v for k, v in node.attrib.items() if k not in ignored}


def main():
    if not __debug__:
        raise SystemExit("Do not run source QA with Python -O; assertions must remain active")
    witnesses = [LANG / f"provenance/m81243.{locale}.cnxml" for locale in ("en", "id-ID")]
    roots = [ET.parse(path).getroot() for path in witnesses]
    module_ids = {n.get("id") for n in roots[0].iter() if n.get("id")}
    source_sections = list(roots[0].find(f"{{{C}}}content"))
    records = []
    for original in source_sections:
        sid = original.get("id")
        path = LANG / f"translation/m81243-{sid}.cnxml"
        title = original.find(f"{{{C}}}title")
        record = {"source_id": sid, "title": "".join(title.itertext()) if title is not None else "section exercises", "source_elements": len(list(original.iter())), "translation_exists": path.is_file()}
        if not path.is_file():
            records.append(record)
            continue
        target = ET.parse(path).getroot()
        assert target.get(XML_LANG) == "ta-Taml-IN", sid
        ids = [n.get("id") for n in target.iter() if n.get("id")]
        assert len(ids) == len(set(ids)), sid
        links = []
        for link in target.findall(f".//{{{C}}}link"):
            target_id, url = link.get("target-id"), link.get("url")
            assert bool(target_id) != bool(url), f"Review link form: {sid}: {link.attrib}"
            if target_id:
                assert target_id in module_ids, f"Unresolved module target: {sid}: {target_id}"
                links.append({"target_id": target_id, "kind": "within-span" if target_id in ids else "cross-span-renderer-must-resolve"})
            else:
                parsed = urlparse(url)
                assert parsed.scheme in ("http", "https") and parsed.netloc, f"Review external URL: {url}"
                links.append({"url": url, "kind": "source-external-link-not-offline-dependency"})
        for root in roots:
            source = root.find(f'.//{{{C}}}section[@id="{sid}"]')
            assert source is not None
            assert [(n.tag, len(n)) for n in source.iter()] == [(n.tag, len(n)) for n in target.iter()], sid
            assert [stable_attributes(n) for n in source.iter()] == [stable_attributes(n) for n in target.iter()], sid
            assert [signature(n) for n in source.findall(f".//{{{M}}}math")] == [signature(n) for n in target.findall(f".//{{{M}}}math")], sid
        assets = []
        for node in target.findall(f".//{{{C}}}image"):
            asset = (path.parent / node.get("src")).resolve()
            assert asset.is_relative_to(LANG / "assets"), asset
            assets.append({"path": asset.relative_to(LANG).as_posix(), "exists": asset.is_file(), "sha256": sha(asset) if asset.is_file() else None})
        record.update({"source_structure_and_math": "pass-against-both-witnesses", "translation_sha256": sha(path), "source_ids": len(ids), "mathml": len(target.findall(f".//{{{M}}}math")), "source_exercises": len(target.findall(f".//{{{C}}}exercise")), "links": links, "media": assets, "all_media_present": all(a["exists"] for a in assets), "reader_status": "not-established-by-this-source-check"})
        records.append(record)
    receipt = {"status": "partial-assignment-source-coverage", "module": "m81243", "complete_module": False, "all_content_spans_structurally_checked": all(r["translation_exists"] for r in records), "witnesses": {p.relative_to(LANG).as_posix(): sha(p) for p in witnesses}, "sections": records, "limits": ["Source prose/number-word accuracy needs linguistic review beyond tree checks", "Glossary, document metadata and other material outside content are not checked here", "Assessment reasoning, rendered accessibility, PDF/EPUB and learner validation are separate", "This report does not imply A10/A20 translation or whole-course routing completion"]}
    (LANG / "qa/source-coverage.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"module": receipt["module"], "translated_spans": sum(r["translation_exists"] for r in records), "total_spans": len(records), "complete_module": receipt["complete_module"]}, indent=2))


if __name__ == "__main__":
    main()
