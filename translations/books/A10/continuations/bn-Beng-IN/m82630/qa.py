"""Deterministic, offline structural and package QA for the bn-Beng-IN m82630 packet."""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse

from lxml import etree as E
from PIL import Image


ROOT = Path(__file__).resolve().parent
CN = "http://cnx.rice.edu/cnxml"
MATHML = "http://www.w3.org/1998/Math/MathML"
NS = {"c": CN}
EXPECTED_STATIC = {
    "source/m82630.en.cnxml": (22483, "d9f45fb31f4cb399c009c2be25eca1a99132b4b6882fb07f8649c2d56974f90b"),
    "source/collection.xml": (5256, "5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72"),
    "media/tryit.png": (344, "7f9c8c226d8b937d4070c69326d6c2ac7df37a74c85fa8cec64e2ad7bef59ebf"),
    "media/howtoicon.png": (1681, "67f2344cdbe25b192fbdee0d904ce912e4e15aed5bf0063f61a192dd0b0b5826"),
    "media/media.png": (353, "140b45d7d047dc59b236c95bb2c2a237ca5b748b290b28f8e6d9f8f520077e6a"),
    "media/CNX_ElemAlg_Figure_05_01_015_img.jpg": (688493, "34fd0299880bc134f6308adcb2296ec1e145431909a1ab1cc2b507e01e3670f4"),
    "LICENSE.txt": (21442, "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"),
}
EXPECTED_IMAGES = {
    "media/tryit.png": ("PNG", (34, 34), "RGB"),
    "media/howtoicon.png": ("PNG", (59, 55), "RGB"),
    "media/media.png": ("PNG", (34, 34), "RGB"),
    "media/CNX_ElemAlg_Figure_05_01_015_img.jpg": ("JPEG", (791, 257), "CMYK"),
}
EXPECTED_TOP_LEVEL = {
    "CHECKSUMS.sha256",
    "DETERMINISTIC_REPLAY.json",
    "EXPERT_REVIEW_LOG.json",
    "LICENSE.txt",
    "MANIFEST.json",
    "OWNER_HANDOFF.md",
    "PACKAGE.json",
    "QA_REPORT.json",
    "SOURCE_RECOVERY.json",
    "TEXT_LEDGER.json",
    "build.py",
    "index.html",
    "media",
    "modules",
    "prepare.py",
    "qa.py",
    "reader.css",
    "seal.py",
    "source",
    "translations.json",
    "visual",
    "visual_check.py",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def load_json(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def text_slots(tree: E._ElementTree):
    result = []
    for el in tree.iter():
        for field in ("text", "tail"):
            value = getattr(el, field)
            if value and value.strip():
                result.append((el, field, value))
    return result


checks: dict[str, dict] = {}


def record(name: str, passed: bool, **details):
    checks[name] = {"status": "pass" if passed else "fail", **details}


def main() -> int:
    for name, (expected_bytes, expected_sha) in EXPECTED_STATIC.items():
        path = ROOT / name
        data = path.read_bytes() if path.is_file() else b""
        record(
            "static:" + name,
            path.is_file() and len(data) == expected_bytes and sha_bytes(data) == expected_sha,
            bytes=len(data),
            sha256=sha_bytes(data),
        )

    source = E.parse(str(ROOT / "source/m82630.en.cnxml"))
    target = E.parse(str(ROOT / "modules/m82630/index.cnxml"))
    mapping = load_json("translations.json")
    source_slots = text_slots(source)
    target_slots = text_slots(target)
    translated = mapping["translations"]
    preserved = mapping["preserve_slots"]
    keys = {str(i) for i in range(len(source_slots))}
    record(
        "text-slot-partition",
        len(source_slots) == 146
        and len(translated) == 119
        and len(preserved) == 27
        and set(translated).isdisjoint(preserved)
        and set(translated) | set(preserved) == keys,
        source_slots=len(source_slots),
        target_slots=len(target_slots),
        translated_slots=len(translated),
        preserved_slots=len(preserved),
    )
    source_nodes = list(source.iter())
    target_nodes = list(target.iter())
    source_node_positions = {id(node): index for index, node in enumerate(source_nodes)}
    values_ok = len(source_nodes) == len(target_nodes)
    for i, (source_node, field, source_value) in enumerate(source_slots):
        expected = translated.get(str(i), source_value)
        node_index = source_node_positions[id(source_node)]
        target_value = getattr(target_nodes[node_index], field)
        if (target_value or "") != expected:
            values_ok = False
    record("text-slot-values", values_ok)

    shape_ok = len(source_nodes) == len(target_nodes)
    attrs_ok = shape_ok
    if shape_ok:
        for left, right in zip(source_nodes, target_nodes):
            if left.tag != right.tag:
                shape_ok = False
            left_attrs = {k: v for k, v in left.attrib.items() if k != "alt"}
            right_attrs = {k: v for k, v in right.attrib.items() if k != "alt"}
            if left_attrs != right_attrs:
                attrs_ok = False
    record("cnxml-element-order-and-tags", shape_ok, source_elements=len(source_nodes), target_elements=len(target_nodes))
    record("cnxml-non-alt-attributes", attrs_ok)

    source_ids = [x.get("id") for x in source.iter() if x.get("id")]
    target_ids = [x.get("id") for x in target.iter() if x.get("id")]
    record(
        "cnxml-ids",
        source_ids == target_ids and len(source_ids) == len(set(source_ids)) == 66,
        source_ids=len(source_ids),
        target_ids=len(target_ids),
        duplicate_ids=len(target_ids) - len(set(target_ids)),
    )

    source_math = source.xpath(f'//*[namespace-uri()="{MATHML}"]')
    target_math = target.xpath(f'//*[namespace-uri()="{MATHML}"]')
    record(
        "mathml-identity",
        len(source_math) == len(target_math) == 0,
        source_mathml_nodes=len(source_math),
        target_mathml_nodes=len(target_math),
        result="The canonical preface contains no MathML; the translation adds or drops none.",
    )

    source_media = {x.get("id"): x for x in source.xpath("//c:media", namespaces=NS)}
    target_media = {x.get("id"): x for x in target.xpath("//c:media", namespaces=NS)}
    alt_ok = set(source_media) == set(target_media) == set(mapping["alt"])
    if alt_ok:
        alt_ok = all(target_media[k].get("alt") == mapping["alt"][k] for k in target_media)
    record("cnxml-media-alt", alt_ok, media_ids=sorted(target_media))

    cnxml_refs = []
    cnxml_refs_ok = True
    for image in target.xpath("//c:image", namespaces=NS):
        rel = image.get("src")
        resolved = (ROOT / "modules/m82630" / rel).resolve()
        cnxml_refs.append({"src": rel, "resolved": resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else None})
        if not resolved.is_relative_to(ROOT) or not resolved.is_file():
            cnxml_refs_ok = False
    record("cnxml-local-assets", cnxml_refs_ok and len(cnxml_refs) == 4, references=cnxml_refs)

    image_results = {}
    image_ok = True
    for name, expected in EXPECTED_IMAGES.items():
        with Image.open(ROOT / name) as image:
            actual = (image.format, image.size, image.mode)
            image.verify()
        image_results[name] = {"format": actual[0], "width": actual[1][0], "height": actual[1][1], "mode": actual[2]}
        image_ok = image_ok and actual == expected
    record("asset-decode-and-geometry", image_ok, images=image_results)

    collection = E.parse(str(ROOT / "source/collection.xml"))
    module_order = collection.xpath('//*[local-name()="module"]/@document')
    record(
        "collection-boundary-and-order",
        len(module_order) == 82 and module_order[:2] == ["m82630", "m82451"] and len(module_order) == len(set(module_order)),
        module_count=len(module_order),
        first=module_order[0] if module_order else None,
        next=module_order[1] if len(module_order) > 1 else None,
    )

    html_tree = E.HTML((ROOT / "index.html").read_text(encoding="utf-8"))
    html_ids = {x.get("id") for x in html_tree.xpath('//*[@id]')}
    local_refs = []
    external_refs = []
    refs_ok = True
    for el in html_tree.xpath('//*[@href or @src]'):
        attr = "href" if el.get("href") is not None else "src"
        value = el.get(attr)
        if value.startswith("#"):
            ok = value[1:] in html_ids
            local_refs.append({"value": value, "exists": ok})
            refs_ok = refs_ok and ok
            continue
        parsed = urlparse(value)
        if parsed.scheme:
            external_refs.append(value)
            ok = parsed.scheme == "https" and parsed.netloc == "github.com"
            refs_ok = refs_ok and ok
            continue
        rel = unquote(value.split("#", 1)[0])
        resolved = (ROOT / rel).resolve()
        ok = resolved.is_relative_to(ROOT) and resolved.is_file()
        local_refs.append({"value": value, "exists": ok})
        refs_ok = refs_ok and ok
    expected_external = [
        "https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m82630/index.cnxml"
    ]
    record("html-local-links-and-urls", refs_ok and external_refs == expected_external, local_references=local_refs, external_references=external_refs)
    html_images = sorted(x.get("src") for x in html_tree.xpath("//img"))
    record("html-image-closure", html_images == sorted(EXPECTED_IMAGES), image_sources=html_images)

    html_text = " ".join(html_tree.itertext())
    credit_markers = [
        "Lynn Marecek, Santa Ana College",
        "MaryAnne Anthony-Smith, Santa Ana College",
        "Andrea Honeycutt Mathis, Northeast Mississippi Community College",
        "John Kalliongis, Saint Louis Iniversity",
        "Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ]
    record("credits-and-attribution", all(x in html_text for x in credit_markers), markers=credit_markers)
    record(
        "reader-scope-label",
        "গোটা ৮২-এককের বই" in html_text and "এখনও সম্পূর্ণ নয়" in html_text and "মূল বইয়ের সম্পূর্ণ মুখবন্ধ" in html_text,
    )
    record(
        "reader-language-and-responsive-css",
        html_tree.xpath("string(/html/@lang)") == "bn-IN"
        and 'name="viewport"' in (ROOT / "index.html").read_text(encoding="utf-8")
        and "@media(max-width:600px)" in (ROOT / "reader.css").read_text(encoding="utf-8"),
    )

    text_extensions = {".py", ".json", ".html", ".css", ".xml", ".cnxml", ".md", ".sha256", ".txt"}
    utf8_results = []
    utf8_ok = True
    no_private_paths = True
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in text_extensions):
        rel = path.relative_to(ROOT).as_posix()
        try:
            value = path.read_bytes().decode("utf-8")
            ok = "\ufffd" not in value and "\x00" not in value
            private_windows = "C:" + "\\Users\\"
            private_posix = "C:" + "/Users/"
            no_private_paths = no_private_paths and private_windows not in value and private_posix not in value
        except UnicodeDecodeError:
            ok = False
        utf8_ok = utf8_ok and ok
        utf8_results.append({"path": rel, "strict_utf8": ok})
    authored_nfc_files = [
        "translations.json",
        "modules/m82630/index.cnxml",
        "index.html",
        "EXPERT_REVIEW_LOG.json",
        "SOURCE_RECOVERY.json",
        "PACKAGE.json",
        "QA_REPORT.json",
        "OWNER_HANDOFF.md",
    ]
    nfc_ok = all(
        (ROOT / name).read_text(encoding="utf-8")
        == unicodedata.normalize("NFC", (ROOT / name).read_text(encoding="utf-8"))
        for name in authored_nfc_files
    )
    record("strict-utf8", utf8_ok, files=utf8_results)
    record("authored-nfc", nfc_ok, files=authored_nfc_files)
    record("no-private-absolute-paths", no_private_paths)

    source_recovery = load_json("SOURCE_RECOVERY.json")
    recovery_media = {x["path"]: (x["bytes"], x["sha256"]) for x in source_recovery["media"]}
    record(
        "source-recovery-crosscheck",
        source_recovery["source"]["sha256"] == sha_path(ROOT / "source/m82630.en.cnxml")
        and source_recovery["authority"]["collection_sha256"] == sha_path(ROOT / "source/collection.xml")
        and all(recovery_media[name] == EXPECTED_STATIC[name] for name in recovery_media)
        and source_recovery["next_module"]["module"] == "m82451",
    )

    review = load_json("EXPERT_REVIEW_LOG.json")
    schema_required = {
        "decision_id",
        "source_location",
        "target_location",
        "source_sense",
        "chosen_wording",
        "authorities_checked",
        "rationale",
        "alternatives",
        "uncertainty",
        "provisional",
        "review_question",
        "rationale_timing",
    }
    review_ok = (
        review.get("schema") == "a10.expert-review-log.v1"
        and review.get("locale") == "bn-Beng-IN"
        and review.get("coverage_status") == "partial"
        and len(review.get("entries", [])) >= 1
        and all(schema_required <= set(x) for x in review["entries"])
        and all(x["authorities_checked"] for x in review["entries"])
        and all(x["rationale_timing"] == "retrospective_reconstruction" for x in review["entries"])
    )
    record("expert-review-schema", review_ok, entries=len(review.get("entries", [])), rationale_timing="retrospective_reconstruction")

    package = load_json("PACKAGE.json")
    core_rows = package.get("core_artifacts", [])
    core_hashes_ok = all(
        (ROOT / row["path"]).is_file()
        and (ROOT / row["path"]).stat().st_size == row["bytes"]
        and sha_path(ROOT / row["path"]) == row["sha256"]
        for row in core_rows
    )
    record(
        "package-scope-and-next",
        package.get("locale") == "bn-Beng-IN"
        and package.get("module") == "m82630"
        and package.get("coverage", {}).get("full_a10_status") == "partial"
        and package.get("next_module", {}).get("module") == "m82451"
        and len(core_rows) == 4
        and core_hashes_ok,
    )

    qa_report = load_json("QA_REPORT.json")
    visual = qa_report.get("browser_visual_review", {})
    record(
        "recorded-browser-visual-review",
        qa_report.get("overall_status") == "pass"
        and visual.get("method") == "captured-headless-chrome-loopback"
        and visual.get("desktop", {}).get("status") == "pass"
        and visual.get("narrow", {}).get("status") == "pass",
        desktop=visual.get("desktop", {}).get("status"),
        narrow=visual.get("narrow", {}).get("status"),
    )

    visual_results = load_json("visual/RESULTS.json")
    visual_inspection = load_json("visual/INSPECTION.json")
    screenshot_rows = visual_results.get("screenshots", [])
    screenshot_hashes_ok = all(
        (ROOT / row["path"]).is_file()
        and (ROOT / row["path"]).stat().st_size == row["bytes"]
        and sha_path(ROOT / row["path"]) == row["sha256"]
        for row in screenshot_rows
    )
    record(
        "visual-evidence-integrity",
        visual_results.get("status") == "pass"
        and visual_inspection.get("status") == "pass"
        and screenshot_hashes_ok
        and len(screenshot_rows) == 4,
        screenshots=len(screenshot_rows),
    )

    replay = load_json("DETERMINISTIC_REPLAY.json")
    record(
        "deterministic-replay",
        replay.get("status") == "pass"
        and replay.get("build_runs") == 2
        and replay.get("visual_runs") == 2
        and replay.get("identical_build_outputs") is True
        and replay.get("identical_visual_outputs") is True,
    )

    actual_top_level = {x.name for x in ROOT.iterdir() if x.name != "__pycache__"}
    record("top-level-inventory", actual_top_level == EXPECTED_TOP_LEVEL, actual=sorted(actual_top_level), expected=sorted(EXPECTED_TOP_LEVEL))

    all_files = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )
    manifest = load_json("MANIFEST.json")
    manifest_rows = manifest.get("files", [])
    manifest_names = [x["path"] for x in manifest_rows]
    expected_manifest_names = [x for x in all_files if x not in {"MANIFEST.json", "CHECKSUMS.sha256"}]
    manifest_ok = (
        manifest.get("schema") == "a10.packet-manifest.v1"
        and manifest_names == expected_manifest_names
        and all((ROOT / x["path"]).stat().st_size == x["bytes"] and sha_path(ROOT / x["path"]) == x["sha256"] for x in manifest_rows)
    )
    record("manifest-integrity", manifest_ok, files=len(manifest_rows))

    checksum_rows = []
    checksums_ok = True
    for line in (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        checksum_rows.append(rel)
        path = ROOT / rel
        checksums_ok = checksums_ok and path.is_file() and sha_path(path) == digest
    expected_checksum_names = [x for x in all_files if x != "CHECKSUMS.sha256"]
    checksums_ok = checksums_ok and checksum_rows == expected_checksum_names and len(checksum_rows) == len(set(checksum_rows))
    record("checksum-integrity", checksums_ok, files=len(checksum_rows))

    passed = all(x["status"] == "pass" for x in checks.values())
    output = {
        "schema": "a10.bn-Beng-IN.qa-runtime.v1",
        "locale": "bn-Beng-IN",
        "module": "m82630",
        "all_passed": passed,
        "checks": checks,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
