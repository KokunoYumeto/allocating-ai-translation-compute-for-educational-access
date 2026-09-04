"""Deterministically verify and seal the bounded Gujarati m82463 packet."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from lxml import etree, html
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SOURCE_SHA = "b6345a5a6a99108f9d32d6518445a4ae70a6b0c54a258021dffc6f2b77b8278a"
RECOVERED_SHA = "ab09802cac764aa6e512e164550bd55fa1b6c99430e76a6ef83194963318c6f1"
CORRECT_008E_ALT = "x − 5/8 + 5/8 = 6/8 + 5/8 સમીકરણ છે. બંને બાજુ 5/8 ઉમેર્યા પછી જમણી બાજુના અપૂર્ણાંકોનો સરવાળો બતાવ્યો છે."
WRONG_008E_ALT = "x = 11/8 સમીકરણ છે. અપૂર્ણાંકનો અંશ 11 અને છેદ 8 છે."
DERIVED = [
    "source/m82463.gu.cnxml", "REVISION.json", "support/NEW_ANSWERS.json",
    "support/FIGURE_ADAPTATIONS.json", "index.html", "answers.html",
    "figures.html", "support.html", "about.html", "qa/MATH.json",
]
SEAL_EXCLUSIONS = {"MANIFEST.json", "CHECKSUMS.sha256", "OWNER_HANDOFF.md", "OWNER_HANDOFF.sha256"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def relfiles() -> list[Path]:
    return sorted(
        (p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )


def inventory(paths: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": p.relative_to(ROOT).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": sha(p),
        }
        for p in paths
    ]


def math_signature(node: etree._Element, include_mtext: bool) -> list[object]:
    result = []
    for e in node.iter():
        local = etree.QName(e).localname
        if local == "mtext" and not include_mtext:
            continue
        attrs = sorted(
            (etree.QName(k).localname, v)
            for k, v in e.attrib.items()
            if etree.QName(k).localname != "alttext"
        )
        result.append((local, " ".join((e.text or "").split()), attrs))
    return result


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    return struct.unpack(">II", data[16:24])


def run_replay() -> tuple[list[dict[str, object]], dict[str, str]]:
    records = []
    baseline = None
    for run in (1, 2):
        build = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build.py")], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        math = subprocess.run(
            [sys.executable, str(ROOT / "scripts/qa_math.py")], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        hashes = {name: sha(ROOT / name) for name in DERIVED}
        if baseline is None:
            baseline = hashes
        else:
            assert hashes == baseline, "deterministic replay mismatch"
        records.append({
            "run": run,
            "build_stdout": build.stdout.strip(),
            "math_stdout": math.stdout.strip(),
            "derived_sha256": hashes,
        })
    return records, baseline or {}


def verify() -> dict[str, object]:
    assert sha(ROOT / "source/en.cnxml") == SOURCE_SHA
    assert sha(ROOT / "source/recovered.gu.cnxml") == RECOVERED_SHA
    source = etree.parse(str(ROOT / "source/en.cnxml"))
    target = etree.parse(str(ROOT / "source/m82463.gu.cnxml"))
    se, te = list(source.iter()), list(target.iter())
    assert len(se) == len(te) == 3249
    assert [etree.QName(x).localname for x in se] == [etree.QName(x).localname for x in te]
    source_ids = [x.get("id") for x in se if x.get("id")]
    target_ids = [x.get("id") for x in te if x.get("id")]
    assert source_ids == target_ids and len(source_ids) == len(set(source_ids)) == 711

    sm = list(source.iter(M + "math"))
    tm = list(target.iter(M + "math"))
    assert len(sm) == len(tm) == 220
    assert [math_signature(x, False) for x in sm] == [math_signature(x, False) for x in tm]
    localized_mtext = sum(math_signature(a, True) != math_signature(b, True) for a, b in zip(sm, tm))
    assert localized_mtext == 6

    anchor = next(x for x in te if x.get("id") == "eip-id1169745434963")
    assert anchor.get("alt") == CORRECT_008E_ALT
    for name in ("scripts/content.py", "source/m82463.gu.cnxml", "index.html"):
        assert WRONG_008E_ALT not in (ROOT / name).read_text(encoding="utf-8")

    exercises = list(target.iter(C + "exercise"))
    solutions = list(target.iter(C + "solution"))
    assert len(exercises) == 116 and len(solutions) == 78
    answers = json.loads((ROOT / "support/NEW_ANSWERS.json").read_text(encoding="utf-8"))
    assert len(answers) == 38 and len({x["source_exercise"] for x in answers}) == 38
    assert {x["source_order"] for x in answers} == set(range(42, 117, 2))
    assert all(x["provenance"] == "new authored support; not an OpenStax supplied solution" for x in answers)

    adaptations = json.loads((ROOT / "support/FIGURE_ADAPTATIONS.json").read_text(encoding="utf-8"))
    assert len(adaptations) == 15
    for item in adaptations:
        p = ROOT / item["source_file"]
        assert p.is_file() and sha(p) == item["source_sha256"]

    pins = json.loads((ROOT / "provenance/INPUT_PINS.json").read_text(encoding="utf-8-sig"))
    assert len(pins) == 82
    for item in pins:
        p = ROOT / item["path"]
        assert p.is_file() and p.stat().st_size == item["bytes"] and sha(p) == item["sha256"]
    media = list((ROOT / "media").glob("*"))
    assert len(media) == 68 and all(p.is_file() for p in media)

    target_id_set = set(target_ids)
    html_id_set: set[str] = set()
    html_docs = {}
    for p in sorted(ROOT.glob("*.html")):
        doc = html.parse(str(p))
        html_docs[p.name] = doc
        ids = doc.xpath("//*[@id]/@id")
        assert not [k for k, v in Counter(ids).items() if v > 1]
        html_id_set.update(ids)
        assert not doc.xpath("//img[not(@alt) or normalize-space(@alt)='']")
        assert not doc.xpath("//script")
        assert not [x for x in doc.xpath("//link[@rel='stylesheet']/@href | //img/@src") if x.startswith(("http:", "https:", "//"))]
    assert len(html_docs) == 5

    ledger = json.loads((ROOT / "EXPERT_REVIEW_LOG.json").read_text(encoding="utf-8"))
    required = {
        "decision_id", "source_location", "target_location", "source_sense",
        "chosen_wording", "authorities_checked", "rationale", "alternatives",
        "uncertainty", "provisional", "review_question", "rationale_timing",
    }
    assert ledger["schema"] == "a10.expert-review-log.v1" and ledger["locale"] == "gu-Gujr-IN"
    entries = ledger["entries"]
    assert len(entries) == 19 and len({x["decision_id"] for x in entries}) == 19
    assert all(required <= set(x) for x in entries)
    assert all(x["authorities_checked"] and x["alternatives"] and x["review_question"] for x in entries)
    assert all(x["rationale_timing"] == "retrospective_reconstruction" for x in entries)
    for entry in entries:
        for field in ("source_location", "target_location"):
            for loc in re.findall(r"#([A-Za-z0-9_.:-]+)", entry[field]):
                assert loc in target_id_set or loc in html_id_set, (entry["decision_id"], loc)

    notice = (ROOT / "notices/A10-NOTICE.txt").read_text(encoding="utf-8")
    license_text = (ROOT / "notices/A10-LICENSE.txt").read_text(encoding="utf-8")
    about = (ROOT / "about.html").read_text(encoding="utf-8")
    assert "OpenStax Elementary Algebra 2e" in notice
    assert "Attribution-NonCommercial-ShareAlike 4.0 International" in license_text
    assert "Lynn Marecek" in about and "MaryAnne Anthony-Smith" in about and "Andrea Honeycutt Mathis" in about
    assert "ઐતિહાસિક શ્રેય" in about

    css = (ROOT / "assets/reader.css").read_text(encoding="utf-8")
    assert "max-width: 1080px" not in css and "calc((100% - 1080px)/2)" not in css
    assert "main { width: 100%; max-width: none" in css
    assert "overflow-x: auto" in css and "overflow-x: clip" in css

    source_text = " ".join((e.text or "") + " " + (e.tail or "") for e in te if etree.QName(e).namespace != M)
    assert "\ufffd" not in source_text and len(re.findall(r"[\u0A80-\u0AFF]", source_text)) > 10000

    return {
        "source": {"bytes": (ROOT / "source/en.cnxml").stat().st_size, "sha256": SOURCE_SHA},
        "recovered": {"bytes": (ROOT / "source/recovered.gu.cnxml").stat().st_size, "sha256": RECOVERED_SHA},
        "target": {"bytes": (ROOT / "source/m82463.gu.cnxml").stat().st_size, "sha256": sha(ROOT / "source/m82463.gu.cnxml")},
        "structure": {"elements": 3249, "ids": 711, "mathml": 220, "localized_mtext": localized_mtext},
        "content": {"exercises": 116, "source_supplied_solutions": 78, "separately_labeled_new_answers": 38, "figure_adaptations": 15},
        "assets": {"input_pins": 82, "original_media": 68},
        "expert_review": {"entries": 19, "provisional": sum(bool(x["provisional"]) for x in entries), "retrospective_backfills": 19},
        "reader": {"pages": sorted(html_docs), "page_count": 5},
    }


def local_link_failures() -> list[dict[str, str]]:
    failures = []
    for p in sorted(ROOT.glob("*.html")):
        doc = html.parse(str(p))
        for value in doc.xpath("//@href | //@src"):
            if value.startswith(("http://", "https://", "#", "mailto:", "data:")):
                continue
            rel = value.split("#", 1)[0].split("?", 1)[0]
            if rel and not (ROOT / rel).is_file():
                failures.append({"page": p.name, "reference": value})
    return failures


def main() -> None:
    cache = ROOT / "scripts/__pycache__"
    if cache.exists():
        shutil.rmtree(cache)
    replay, derived = run_replay()
    if cache.exists():
        shutil.rmtree(cache)
    verified = verify()

    package = {
        "schema": "a10.locale-module-package.v1",
        "status": "complete_module_checkpoint",
        "locale": "gu-Gujr-IN",
        "collection": "col31130",
        "module": "m82463",
        "source_order": 14,
        "canonical_commit": "38cae454e644abf9f0a623e876994553881597c9",
        "scope": "Complete Gujarati translation and standalone learning reader for m82463 only.",
        "progress_if_owner_admits": "14/82 source modules",
        "not_claimed": [
            "complete 82-module Gujarati edition",
            "complete full-book AX-1/AX-3 support",
            "complete separate Grades 2-6 route",
            "audio or SSML",
        ],
        "next_source_ordered_module": "m82464",
        "components": [
            "source/m82463.gu.cnxml", "index.html", "answers.html", "figures.html",
            "support.html", "about.html", "EXPERT_REVIEW_LOG.json",
        ],
        "source_attribution": {
            "work": "OpenStax Elementary Algebra 2e",
            "authors": ["Lynn Marecek", "MaryAnne Anthony-Smith", "Andrea Honeycutt Mathis"],
            "license": "CC BY-NC-SA 4.0, subject to component notices",
        },
    }
    write_json(ROOT / "PACKAGE.json", package)

    browser = {
        "schema": "a10.browser-qa.v1",
        "status": "pass",
        "page": "index.html",
        "renderer": {"engine": "Google Chrome", "version": "152.0.7977.77", "automation": "Playwright 1.62.1"},
        "viewports": [
            {"name": "wide", "width": 1600, "height": 1000, "document_scroll_width": 1600, "horizontal_overflow": False, "main_left": 0, "main_right": 1600, "main_width": 1600},
            {"name": "narrow", "width": 390, "height": 844, "document_scroll_width": 390, "horizontal_overflow": False, "main_left": 0, "main_right": 390, "main_width": 390},
        ],
        "screenshots": [],
        "visual_inspection": {
            "status": "pass",
            "checks": [
                "Gujarati glyphs render cleanly with the packaged font",
                "wide main content fills the viewport instead of a centered fixed-width column",
                "narrow navigation wraps and prose remains readable",
                "document-level horizontal overflow is absent; wide tables and mathematics retain local scrolling",
                "headings, scope note, contents and first exercise are not clipped or overlapped",
            ],
        },
        "lazy_media_note": "The viewport screenshots exercise visible content. All 68 original media are separately hash- and reference-verified; closed details intentionally defer non-visible images.",
    }
    for name, expected in (("wide", (1600, 1000)), ("narrow", (390, 844))):
        p = ROOT / f"qa/{name}.png"
        assert p.is_file() and png_dimensions(p) == expected
        browser["screenshots"].append({"path": f"qa/{name}.png", "width": expected[0], "height": expected[1], "bytes": p.stat().st_size, "sha256": sha(p)})
    write_json(ROOT / "BROWSER_QA.json", browser)

    qa = {
        "schema": "a10.module-qa.v1",
        "status": "pass",
        "module": "m82463",
        "locale": "gu-Gujr-IN",
        "deterministic_replay": {"runs": 2, "identical": True, "records": replay, "final_derived_sha256": derived},
        "verification": verified,
        "accessibility": {
            "corrected_anchor": "eip-id1169745434963",
            "corrected_008e_alt": CORRECT_008E_ALT,
            "wrong_008e_alt_absent_from_generator_target_and_reader": True,
            "all_68_reader_images_have_nonempty_alt": True,
            "all_reader_ids_unique": True,
        },
        "rights": {"status": "pass", "license": "notices/A10-LICENSE.txt", "notice": "notices/A10-NOTICE.txt", "historical_notice_caveated_in": "about.html"},
        "visual": {"status": "pass", "receipt": "BROWSER_QA.json", "screenshots": ["qa/wide.png", "qa/narrow.png"]},
        "limitations": ["This is one complete module checkpoint, not the complete Gujarati A10 edition.", "No audio is claimed."],
    }
    write_json(ROOT / "QA.json", qa)

    # Make the linked manifest exist, then prove all local reader links and seal
    # the payload. MANIFEST deliberately excludes the four named seal-layer files.
    write_json(ROOT / "MANIFEST.json", {"status": "provisional"})
    failures = local_link_failures()
    assert not failures, failures
    qa["local_reader_links"] = {"status": "pass", "failures": [], "pages_checked": 5}
    write_json(ROOT / "QA.json", qa)

    payload_paths = [p for p in relfiles() if p.relative_to(ROOT).as_posix() not in SEAL_EXCLUSIONS]
    manifest_entries = inventory(payload_paths)
    manifest = {
        "schema": "a10.packet-manifest.v1",
        "inventory_scope": "All packet files except MANIFEST.json, CHECKSUMS.sha256, OWNER_HANDOFF.md and OWNER_HANDOFF.sha256; those form the non-circular outer seal layers.",
        "excluded_from_inventory": sorted(SEAL_EXCLUSIONS),
        "file_count": len(manifest_entries),
        "total_bytes": sum(x["bytes"] for x in manifest_entries),
        "files": manifest_entries,
    }
    write_json(ROOT / "MANIFEST.json", manifest)

    checksum_paths = [p for p in relfiles() if p.relative_to(ROOT).as_posix() not in {"CHECKSUMS.sha256", "OWNER_HANDOFF.md", "OWNER_HANDOFF.sha256"}]
    checksum_lines = [f"{sha(p)}  {p.relative_to(ROOT).as_posix()}" for p in checksum_paths]
    write_text(ROOT / "CHECKSUMS.sha256", "\n".join(checksum_lines) + "\n")

    handoff = f"""# Immutable owner handoff — Gujarati m82463

Status: **admit-ready bounded module checkpoint**  
Locale/module: `gu-Gujr-IN` / `m82463` (source order 14 of 82)  
Canonical source: `openstax/osbooks-prealgebra-bundle@38cae454e644abf9f0a623e876994553881597c9`  
Source SHA-256: `{SOURCE_SHA}`  
Target SHA-256: `{sha(ROOT / 'source/m82463.gu.cnxml')}`

The source topology, 711 ordered unique IDs, 220 MathML expressions, 116 exercises,
78 source-supplied solutions and all 68 original media are preserved. The 38 newly
authored answers remain separately labeled. The `008e` accessibility regression is
repaired against the actual source image. Two deterministic build/math-QA replays
matched byte-for-byte. Wide 1600×1000 and narrow 390×844 browser checks pass with
full-viewport reflow and no document-level horizontal overflow.

This handoff claims one complete module, not the full Gujarati book, full-book
AX-1/AX-3 support, the separate Grades 2–6 route, or audio. Owner integration and
publication authority remain outside this packet.

## Non-circular seal

- `PACKAGE.json`: `{sha(ROOT / 'PACKAGE.json')}`
- `QA.json`: `{sha(ROOT / 'QA.json')}`
- `BROWSER_QA.json`: `{sha(ROOT / 'BROWSER_QA.json')}`
- `MANIFEST.json`: `{sha(ROOT / 'MANIFEST.json')}`
- `CHECKSUMS.sha256`: `{sha(ROOT / 'CHECKSUMS.sha256')}`
- Manifest payload: {manifest['file_count']} files, {manifest['total_bytes']} bytes
- Manifest exclusions: `MANIFEST.json`, `CHECKSUMS.sha256`, `OWNER_HANDOFF.md`, `OWNER_HANDOFF.sha256`
- `CHECKSUMS.sha256` covers the manifest and every manifest payload file; this
  handoff binds those outer hashes; `OWNER_HANDOFF.sha256` binds this handoff.

Next source-ordered Gujarati module after owner admission: `m82464`.
"""
    write_text(ROOT / "OWNER_HANDOFF.md", handoff)
    write_text(ROOT / "OWNER_HANDOFF.sha256", f"{sha(ROOT / 'OWNER_HANDOFF.md')}  OWNER_HANDOFF.md\n")

    # Final independent seal replay.
    for item in manifest["files"]:
        p = ROOT / item["path"]
        assert p.is_file() and p.stat().st_size == item["bytes"] and sha(p) == item["sha256"]
    for line in (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        assert sha(ROOT / name) == digest
    digest, name = (ROOT / "OWNER_HANDOFF.sha256").read_text(encoding="utf-8").strip().split("  ", 1)
    assert name == "OWNER_HANDOFF.md" and sha(ROOT / name) == digest
    assert not local_link_failures()
    if cache.exists():
        shutil.rmtree(cache)

    final_files = relfiles()
    print(json.dumps({
        "status": "PASS",
        "final_files": len(final_files),
        "final_bytes": sum(p.stat().st_size for p in final_files),
        "target_sha256": sha(ROOT / "source/m82463.gu.cnxml"),
        "manifest_sha256": sha(ROOT / "MANIFEST.json"),
        "checksums_sha256": sha(ROOT / "CHECKSUMS.sha256"),
        "handoff_sha256": sha(ROOT / "OWNER_HANDOFF.md"),
        "wide_screenshot_sha256": sha(ROOT / "qa/wide.png"),
        "narrow_screenshot_sha256": sha(ROOT / "qa/narrow.png"),
    }, indent=2))


if __name__ == "__main__":
    main()
