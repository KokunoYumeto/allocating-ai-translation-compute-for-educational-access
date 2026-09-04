"""Deterministic admission QA for the bounded m82453 Javanese packet."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from lxml import etree as E

sys.dont_write_bytecode = True
from wording import COMMON, SPECIAL

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
NS = {"c": CN, "m": M}
SOURCE_HASH = "f8b281215e7630e8425e26bd28d54b26ed707fe9840bfb2edd417d40da666d9f"
PIVOT_HASH = "8acbc36596af0f7552f4b50268452c083137ba9b58979385511e4cc3f7b240e3"
ZIP_HASH = "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456"
MEMBER_HASH = "2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635"
LICENSE_HASH = "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"
TRACKS = ["jv-academic", "jv-conversation", "id-academic"]
checks: list[dict] = []


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check(name: str, condition: bool, detail) -> None:
    checks.append({"name": name, "passed": bool(condition), "detail": detail})


def qname(node) -> str:
    return E.QName(node).localname


def parse(path: Path):
    return E.parse(str(path)).getroot()


def structural(root) -> dict:
    nodes = list(root.iter())
    ids = [node.get("id") for node in nodes if node.get("id")]
    return {
        "elements": len(nodes),
        "tags": [qname(node) for node in nodes],
        "ids": ids,
        "mathml": len(root.xpath('.//*[local-name()="math"]')),
        "exercises": len(root.xpath('.//*[local-name()="exercise"]')),
        "solutions": len(root.xpath('.//*[local-name()="solution"]')),
        "media": len(root.xpath('.//*[local-name()="media"]')),
    }


def math_signature(root) -> list:
    result = []
    for math in root.xpath('.//*[local-name()="math"]'):
        one = []
        for node in math.iter():
            name = qname(node)
            attrs = tuple(sorted((qname_attr.split('}')[-1], value) for qname_attr, value in node.attrib.items()))
            protected_text = (node.text or "") if name in {"mi", "mn", "mo"} else None
            one.append((name, attrs, protected_text))
        result.append(one)
    return result


# Frozen authorities and archive closure.
source_path = ROOT / "source/en.cnxml"
pivot_path = ROOT / "source/id-pivot.cnxml"
zip_path = ROOT / "source/pivot-source.zip"
check("frozen English source hash", sha(source_path) == SOURCE_HASH, sha(source_path))
check("frozen Indonesian pivot hash", sha(pivot_path) == PIVOT_HASH, sha(pivot_path))
check("pinned Indonesian source ZIP hash", sha(zip_path) == ZIP_HASH, sha(zip_path))
with zipfile.ZipFile(zip_path) as archive:
    bad = archive.testzip()
    member = archive.read("translated/modules/m82453/index.cnxml")
    license_member = archive.read("LICENSE.txt")
check("pivot ZIP CRC and exact members", bad is None and hashlib.sha256(member).hexdigest() == MEMBER_HASH and hashlib.sha256(license_member).hexdigest() == LICENSE_HASH, {"bad_member": bad, "module_sha256": hashlib.sha256(member).hexdigest(), "license_sha256": hashlib.sha256(license_member).hexdigest()})
check("exact local license", (ROOT / "LICENSE.txt").is_file() and sha(ROOT / "LICENSE.txt") == LICENSE_HASH, sha(ROOT / "LICENSE.txt") if (ROOT / "LICENSE.txt").exists() else "missing")

boundary = json.loads((ROOT / "source/BOUNDARY.json").read_text(encoding="utf-8"))
asset_results = []
for record in boundary["media"]:
    artifact = ROOT / record["file"]
    actual = {"file": record["file"], "bytes": artifact.stat().st_size if artifact.exists() else None, "sha256": sha(artifact) if artifact.exists() else None}
    actual["passed"] = artifact.exists() and actual["bytes"] == record["bytes"] and actual["sha256"] == record["sha256"]
    asset_results.append(actual)
check("three canonical assets", len(asset_results) == 3 and all(item["passed"] for item in asset_results), asset_results)

# Replay authored outputs and prove byte stability.
generated = [
    "translation/jv-academic.cnxml", "translation/jv-conversation.cnxml", "translation/id-academic.cnxml",
    "provenance/TRANSLATION-SLOTS.json", "index.html", "jv-academic.html", "jv-conversation.html",
    "id-academic.html", "en.html", "narration/jv-academic.md", "narration/jv-academic.ssml",
    "narration/jv-conversation.md", "narration/jv-conversation.ssml", "narration/id-academic.md",
    "narration/id-academic.ssml",
]
before = {name: sha(ROOT / name) for name in generated}
replay_output = []
for script in ["draft.py", "build.py"]:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, text=True, encoding="utf-8", capture_output=True)
    replay_output.append({"script": script, "returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()})
    if result.returncode:
        break
after = {name: sha(ROOT / name) for name in generated if (ROOT / name).exists()}
check("draft/build deterministic replay", all(item["returncode"] == 0 for item in replay_output) and before == after, {"runs": replay_output, "output_count": len(after), "changed": sorted(name for name in before if before.get(name) != after.get(name))})

# CNXML structure, IDs, math, source slots, and target semantics.
source = parse(source_path)
source_structure = structural(source)
check("source boundary counts", source_structure["elements"] == 669 and len(source_structure["ids"]) == 106 and source_structure["mathml"] == 63 and source_structure["exercises"] == 15 and source_structure["solutions"] == 15 and source_structure["media"] == 3, source_structure)
source_math = math_signature(source)
targets = {track: parse(ROOT / "translation" / f"{track}.cnxml") for track in TRACKS}
structure_results = {}
for track, target in targets.items():
    shape = structural(target)
    structure_results[track] = {
        "elements": shape["elements"],
        "ids": len(shape["ids"]),
        "mathml": shape["mathml"],
        "exercises": shape["exercises"],
        "solutions": shape["solutions"],
        "media": shape["media"],
        "same_tag_order": shape["tags"] == source_structure["tags"],
        "same_id_order": shape["ids"] == source_structure["ids"],
        "same_protected_math": math_signature(target) == source_math,
    }
check("all target structures, IDs, and protected math", all(item["elements"] == 669 and item["ids"] == 106 and item["mathml"] == 63 and item["exercises"] == 15 and item["solutions"] == 15 and item["media"] == 3 and item["same_tag_order"] and item["same_id_order"] and item["same_protected_math"] for item in structure_results.values()), structure_results)

slots = json.loads((ROOT / "source/text-slots.json").read_text(encoding="utf-8"))
ledger = json.loads((ROOT / "provenance/TRANSLATION-SLOTS.json").read_text(encoding="utf-8"))
slot_counts = Counter(record["track"] for record in ledger["records"])
slot_mismatches = []
for track_number, track in enumerate(["jv-academic", "jv-conversation"]):
    nodes = list(targets[track].iter())
    for slot_number, slot in enumerate(slots):
        expected = SPECIAL[slot_number][track_number] if slot_number in SPECIAL else COMMON.get(slot["source"], (slot["source"], slot["source"]))[track_number]
        node = nodes[slot["node"]]
        actual = node.get(slot["field"][1:]) if slot["field"].startswith("@") else getattr(node, slot["field"])
        if actual is None or actual.strip() != expected.strip():
            slot_mismatches.append({"track": track, "slot": slot_number, "expected": expected, "actual": actual.strip() if actual else None})
check("206 current source slots per Javanese track", len(slots) == 206 and slot_counts == Counter({"jv-academic": 206, "jv-conversation": 206}) and not slot_mismatches, {"source_slots": len(slots), "ledger_records": dict(slot_counts), "mismatches": slot_mismatches})
id_revisions = ledger["indonesian_bridge"]["revisions"]
check("bounded Indonesian revisions recorded", len(id_revisions) == 67 and len({item["slot"] for item in id_revisions}) == 67, {"count": len(id_revisions), "slots": [item["slot"] for item in id_revisions]})

localized_text = "\n".join("".join(root.itertext()) for root in targets.values())
forbidden = ["andkanggo", "andsupaya", "saka saka", "tembungof", "kataof", "luwih akèh tinimbang", "luwih sithik tinimbang", "lebih banyak daripada", "lebih sedikit daripada", "lebih kecil daripada", "\ufffd"]
present = [term for term in forbidden if term in localized_text]
check("no malformed joins or comparative-operation wording", not present, present)
operation_evidence = {
    "jv-academic": ["Pitulas ditambahaké marang", "Sanga dikurangaké saka", "telu dikurangaké saka papat ping"],
    "jv-conversation": ["Pitulas ditambahké menyang", "Sanga dijupuk saka", "telu dijupuk saka papat ping"],
    "id-academic": ["Tujuh belas ditambahkan pada", "Sembilan dikurangkan dari", "tiga dikurangkan dari empat kali"],
}
operation_result = {track: [phrase in "".join(targets[track].itertext()) for phrase in phrases] for track, phrases in operation_evidence.items()}
check("explicit operand-order language", all(all(values) for values in operation_result.values()), operation_result)
punctuation = {}
for track in ["jv-academic", "jv-conversation"]:
    maths = targets[track].xpath('(//*[@id="eip-470"]//*[local-name()="math"])')
    punctuation[track] = {"math_count": len(maths), "third_tail": maths[2].tail if len(maths) >= 3 else None}
check("eip-470 asserted third-math punctuation", all(item["math_count"] == 5 and item["third_tail"] == "”." for item in punctuation.values()), punctuation)

# Narration, actual audio, expert review, model provenance, and package truth.
narration_results = {}
for track in TRACKS:
    ssml_path = ROOT / "narration" / f"{track}.ssml"
    ssml = parse(ssml_path)
    expected_lang = "jv-Latn-ID" if track.startswith("jv") else "id-ID"
    marks = ssml.findall("mark")
    paragraphs = ssml.findall("p")
    md = (ROOT / "narration" / f"{track}.md").read_text(encoding="utf-8")
    narration_results[track] = {
        "lang": ssml.get("{http://www.w3.org/XML/1998/namespace}lang"),
        "marks": len(marks),
        "paragraphs": len(paragraphs),
        "unique_marks": len({mark.get("name") for mark in marks}),
        "answer_labels": md.count("Wangsulan saka sumber") if track.startswith("jv") else md.count("Jawaban dari sumber"),
        "sha256": sha(ssml_path),
        "passed": ssml.get("{http://www.w3.org/XML/1998/namespace}lang") == expected_lang and len(marks) == 23 and len(paragraphs) == 23 and len({mark.get("name") for mark in marks}) == 23 and (md.count("Wangsulan saka sumber") if track.startswith("jv") else md.count("Jawaban dari sumber")) == 15,
    }
check("source-positioned narration and SSML", all(item["passed"] for item in narration_results.values()), narration_results)

audio = json.loads((ROOT / "audio/AUDIO.json").read_text(encoding="utf-8"))
audio_results = {}
for track, voice in [("jv-academic", "jv-ID-DimasNeural"), ("jv-conversation", "jv-ID-SitiNeural")]:
    record = audio["tracks"][track]
    artifact = ROOT / record["file"]
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,channels:format=duration", "-of", "json", str(artifact)], capture_output=True, text=True, encoding="utf-8")
    probe_data = json.loads(probe.stdout) if probe.returncode == 0 else {}
    stream = probe_data.get("streams", [{}])[0]
    actual_duration = round(float(probe_data.get("format", {}).get("duration", 0)), 3)
    audio_results[track] = {
        "file": record["file"], "bytes": artifact.stat().st_size if artifact.exists() else None,
        "sha256": sha(artifact) if artifact.exists() else None, "voice": record["voice"],
        "voice_locale": record["voice_locale"], "duration_seconds": actual_duration,
        "passed": artifact.exists() and sha(artifact) == record["sha256"] and artifact.stat().st_size == record["bytes"] and record["voice"] == voice and record["voice_locale"] == "jv-ID" and record["narration_ssml_sha256"] == narration_results[track]["sha256"] and stream.get("codec_name") == "mp3" and int(stream.get("sample_rate", 0)) == 24000 and int(stream.get("channels", 0)) == 1 and actual_duration == record["duration_seconds"] and actual_duration > 60,
    }
check("actual genuine-locale Javanese audio", audio.get("locale") == "jv-Latn-ID" and audio.get("human_recording") is False and all(item["passed"] for item in audio_results.values()), audio_results)

expert = json.loads((ROOT / "EXPERT_REVIEW_LOG.json").read_text(encoding="utf-8"))
required = {"decision_id", "source_location", "target_location", "source_sense", "chosen_wording", "authorities_checked", "rationale", "alternatives", "uncertainty", "provisional", "review_question", "rationale_timing"}
expert_ok = expert.get("schema") == "a10.expert-review-log.v1" and expert.get("locale") == "jv-Latn-ID" and expert.get("coverage_status") == "partial" and len(expert.get("entries", [])) >= 1 and all(required <= set(entry) and entry["authorities_checked"] and entry["rationale_timing"] in {"contemporaneous", "retrospective_reconstruction"} for entry in expert["entries"])
check("honest provisional expert-review ledger", expert_ok and all(entry["provisional"] is True for entry in expert["entries"]), {"entries": len(expert.get("entries", [])), "status": expert.get("review_status")})
model_text = (ROOT / "provenance/MODEL.md").read_text(encoding="utf-8")
check("exact model provenance", "OpenAI Codex gpt-5.6-sol, Ultra" in model_text and ledger.get("model") == "OpenAI Codex gpt-5.6-sol, Ultra", "OpenAI Codex gpt-5.6-sol, Ultra")
package = json.loads((ROOT / "PACKAGE.json").read_text(encoding="utf-8"))
check("truthful bounded package scope", package["coverage"]["source_slots_per_track"] == 206 and "not a complete module or book" in package["coverage"]["truth"] and package["audio"]["fallback_locale_used"] is False and package["indonesian_bridge"]["bounded_revisions"] == 67, {"status": package["status"], "coverage": package["coverage"]["truth"]})

# Offline reader/link/browser closure.
reader_results = {}
seal_files = {"QA.json", "MANIFEST.json", "CHECKSUMS.sha256", "OWNER_HANDOFF.json"}
for file in ["index.html", "jv-academic.html", "jv-conversation.html", "id-academic.html", "en.html"]:
    root = E.HTML((ROOT / file).read_text(encoding="utf-8"))
    missing = []
    for value in root.xpath('//a/@href | //img/@src | //audio/@src'):
        if value.startswith(("http://", "https://", "#")):
            continue
        target_name = value.split("#", 1)[0]
        if not target_name or Path(target_name).name in seal_files:
            continue
        if not (ROOT / target_name).exists():
            missing.append(value)
    reader_results[file] = {
        "mathml": len(root.xpath('//*[local-name()="math"]')),
        "tables": len(root.xpath('//table')),
        "figures": len(root.xpath('//figure')),
        "source_links": len(root.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " source-link ")]//a')),
        "audio": len(root.xpath('//audio')),
        "missing_local_links": missing,
    }
reader_ok = all(not item["missing_local_links"] for item in reader_results.values()) and all(reader_results[file]["mathml"] == 63 and reader_results[file]["tables"] == 3 and reader_results[file]["figures"] == 3 for file in reader_results if file != "index.html") and all(reader_results[file]["source_links"] == 15 for file in ["jv-academic.html", "jv-conversation.html", "id-academic.html"]) and reader_results["jv-academic.html"]["audio"] == 1 and reader_results["jv-conversation.html"]["audio"] == 1
check("offline reader and link closure", reader_ok, reader_results)
css = (ROOT / "reader.css").read_text(encoding="utf-8")
check("wide reflow without centered cap", "max-width:990px" not in css.replace(" ", "") and "width: 100%" in css, {"css_sha256": sha(ROOT / "reader.css")})
browser = json.loads((ROOT / "BROWSER_QA.json").read_text(encoding="utf-8"))
screenshot_results = []
for record in browser.get("screenshots", []):
    artifact = ROOT / record["file"]
    screenshot_results.append({"file": record["file"], "passed": artifact.exists() and artifact.stat().st_size == record["bytes"] and sha(artifact) == record["sha256"], "bytes": artifact.stat().st_size if artifact.exists() else None, "sha256": sha(artifact) if artifact.exists() else None})
check("browser QA and inspected screenshot evidence", browser.get("status") == "pass" and len(browser.get("checks", [])) == 10 and all(item.get("passed") for item in browser.get("checks", [])) and len(screenshot_results) == 4 and all(item["passed"] for item in screenshot_results), {"browser_status": browser.get("status"), "screenshots": screenshot_results})

status = "pass" if all(item["passed"] for item in checks) else "fail"
result = {
    "schema": "a10.bounded-admission-qa.v1",
    "date": "2026-09-04",
    "scope": "m82453/fs-id1170654942537",
    "status": status,
    "check_count": len(checks),
    "passed_count": sum(item["passed"] for item in checks),
    "checks": checks,
}
(ROOT / "QA.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"QA {status}: {result['passed_count']}/{result['check_count']} checks passed.")
if status != "pass":
    for item in checks:
        if not item["passed"]:
            print(f"FAIL {item['name']}: {item['detail']}")
    raise SystemExit(1)
