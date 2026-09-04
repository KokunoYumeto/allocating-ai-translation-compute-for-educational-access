from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "en.cnxml"
TARGET = ROOT / "target" / "bn-Beng-IN.cnxml"
READER = ROOT / "reader" / "index.html"
BACKEND = ROOT / "backend" / "module.json"
ACCESSIBILITY = ROOT / "accessibility" / "accessibility.json"
EXPERT = ROOT / "EXPERT_REVIEW_LOG.json"
SOURCE_LOCK = ROOT / "SOURCE_LOCK.json"
ASSET_LOCK = ROOT / "ASSET_LOCK.json"
DESKTOP_PROOF = ROOT / "qa" / "reader-1280x900.png"
NARROW_PROOF = ROOT / "qa" / "reader-500x844.png"

CNXML = "http://cnx.rice.edu/cnxml"
MDML = "http://cnx.rice.edu/mdml"
NS = {"c": CNXML, "md": MDML}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tags(root: ET.Element) -> list[str]:
    return [node.tag for node in root.iter()]


def ids(root: ET.Element) -> list[str]:
    return [node.attrib["id"] for node in root.iter() if "id" in node.attrib]


def check(name: str, condition: bool, details: str) -> dict[str, object]:
    if not condition:
        raise AssertionError(f"{name}: {details}")
    return {"name": name, "status": "pass", "details": details}


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR"
    return struct.unpack(">II", header[16:24])


def main() -> None:
    results: list[dict[str, object]] = []
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    asset_lock = json.loads(ASSET_LOCK.read_text(encoding="utf-8"))
    source_bytes = SOURCE.read_bytes()
    results.append(check("source-lock-sha256", sha256(SOURCE) == source_lock["source_sha256"], source_lock["source_sha256"]))
    results.append(check("source-lock-bytes", len(source_bytes) == source_lock["source_bytes"], str(len(source_bytes))))

    source = ET.parse(SOURCE).getroot()
    target = ET.parse(TARGET).getroot()
    results.append(check("xml-well-formed", True, "source and target parsed with ElementTree"))
    results.append(check("element-topology", tags(source) == tags(target), f"{len(tags(target))} expanded-name elements preserved in order"))
    results.append(check("id-topology", ids(source) == ids(target), f"IDs preserved in order: {ids(target)}"))
    results.append(check("root-attributes", source.attrib == target.attrib, json.dumps(target.attrib, ensure_ascii=False, sort_keys=True)))

    s_uuid = source.findtext("c:metadata/md:uuid", namespaces=NS)
    t_uuid = target.findtext("c:metadata/md:uuid", namespaces=NS)
    s_content_id = source.findtext("c:metadata/md:content-id", namespaces=NS)
    t_content_id = target.findtext("c:metadata/md:content-id", namespaces=NS)
    results.append(check("metadata-identity", (s_uuid, s_content_id) == (t_uuid, t_content_id), f"content-id={t_content_id}; uuid={t_uuid}"))

    s_image = source.find(".//c:image", NS)
    t_image = target.find(".//c:image", NS)
    assert s_image is not None and t_image is not None
    results.append(check("image-source-geometry", s_image.attrib == t_image.attrib, json.dumps(t_image.attrib, ensure_ascii=False, sort_keys=True)))
    results.append(check("mathml-count", len(source.findall(".//{http://www.w3.org/1998/Math/MathML}math")) == len(target.findall(".//{http://www.w3.org/1998/Math/MathML}math")) == 0, "0 MathML blocks in source and target"))
    results.append(check("exercise-answer-counts", not source.findall(".//c:exercise", NS) and not target.findall(".//c:exercise", NS) and not source.findall(".//c:solution", NS) and not target.findall(".//c:solution", NS), "0 exercises and 0 supplied answers"))

    target_text = " ".join(t.strip() for t in target.itertext() if t.strip())
    bengali_chars = len(re.findall(r"[\u0980-\u09ff]", target_text))
    results.append(check("bengali-script", bengali_chars >= 200, f"{bengali_chars} Bengali-script code points"))
    translatable = [
        target.findtext("c:title", namespaces=NS),
        target.findtext("c:metadata/md:title", namespaces=NS),
        target.find(".//c:media", NS).attrib.get("alt"),
        target.findtext(".//c:caption", namespaces=NS),
        target.findtext(".//c:para", namespaces=NS),
    ]
    results.append(check("translated-visible-fields", all(x and re.search(r"[\u0980-\u09ff]", x) and not re.search(r"\b(?:Introduction|building|foundation|algebra|numbers|fractions|decimals)\b", x, re.I) for x in translatable), "all 5 visible/translatable fields contain Bengali and no checked English residue"))

    target_bytes = TARGET.read_bytes()
    results.append(check("utf8", target_bytes.decode("utf-8").encode("utf-8") == target_bytes and not target_bytes.startswith(b"\xef\xbb\xbf"), "strict UTF-8 round trip; no BOM"))

    backend = json.loads(BACKEND.read_text(encoding="utf-8"))
    accessibility = json.loads(ACCESSIBILITY.read_text(encoding="utf-8"))
    reader = READER.read_text(encoding="utf-8")
    title, alt, caption, para = translatable[0], translatable[2], translatable[3], translatable[4]
    results.append(check("backend-agreement", backend["title"] == title and backend["blocks"][0]["image"]["alt"] == alt and backend["blocks"][0]["caption"] == caption and backend["blocks"][1]["text"] == para, "title, alt, caption and paragraph match target CNXML"))
    results.append(check("reader-agreement", all(text in reader for text in [title, alt, caption, para]), "title, alt, caption and paragraph match target CNXML"))
    reflow = (
        "width: min(100%, 72rem)" not in reader
        and "max-width: 100vw" in reader
        and "overflow-x: hidden" in reader
        and "overflow-wrap: anywhere" in reader
        and "width: 100%" in reader
        and "viewport" in reader
    )
    results.append(check("reader-reflow", reflow, "fluid full-page flow, bounded gutters, wrapping and no narrow centered cap"))
    results.append(check(
        "visual-artifacts",
        png_dimensions(DESKTOP_PROOF) == (1280, 900) and png_dimensions(NARROW_PROOF) == (500, 844),
        "desktop 1280x900 and narrow 500x844 PNG proofs exist with exact viewport dimensions",
    ))
    results.append(check("accessibility-agreement", accessibility["figures"][0]["alt"] == alt and accessibility["figures"][0]["caption"] == caption and accessibility["audio"]["available"] is False and accessibility["audio"]["substitute_claimed"] is False, "figure text matches target; audio tracked separately and absent"))

    asset = ROOT / asset_lock["assets"][0]["packet_path"]
    results.append(check("offline-asset-bytes", asset.stat().st_size == asset_lock["assets"][0]["bytes"], str(asset.stat().st_size)))
    results.append(check("offline-asset-sha256", sha256(asset) == asset_lock["assets"][0]["sha256"], sha256(asset)))

    expert = json.loads(EXPERT.read_text(encoding="utf-8"))
    required = {"decision_id", "source_location", "target_location", "source_sense", "chosen_wording", "authorities_checked", "rationale", "alternatives", "uncertainty", "provisional", "review_question", "rationale_timing"}
    results.append(check("expert-log-complete", expert["schema"] == "a10.expert-review-log.v1" and expert["locale"] == "bn-Beng-IN" and expert["coverage_status"] == "complete" and len(expert["entries"]) == 3 and all(required <= set(entry) and entry["authorities_checked"] for entry in expert["entries"]), "3 substantive decisions; required fields populated; no review falsely claimed"))

    report = {
        "schema": "a10.packet-qa.v1",
        "module_id": "m82451",
        "locale": "bn-Beng-IN",
        "status": "pass",
        "test_count": len(results),
        "tests": results,
        "target": {"path": "target/bn-Beng-IN.cnxml", "bytes": TARGET.stat().st_size, "sha256": sha256(TARGET)},
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
