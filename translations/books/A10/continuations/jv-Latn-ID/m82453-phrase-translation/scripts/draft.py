"""Build the three target CNXML tracks from the frozen section witnesses."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

from lxml import etree as E

sys.dont_write_bytecode = True
from wording import COMMON, SPECIAL

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCE_SHA256 = "f8b281215e7630e8425e26bd28d54b26ed707fe9840bfb2edd417d40da666d9f"
EXPECTED_PIVOT_SHA256 = "8acbc36596af0f7552f4b50268452c083137ba9b58979385511e4cc3f7b240e3"
TRACKS = ["jv-academic", "jv-conversation"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def atomic_text(path: Path, text: str) -> None:
    atomic_bytes(path, text.replace("\r\n", "\n").encode("utf-8"))


source_bytes = (ROOT / "source/en.cnxml").read_bytes()
if sha256_bytes(source_bytes) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Frozen English section hash mismatch")
source = E.fromstring(source_bytes)
slots = json.loads((ROOT / "source/text-slots.json").read_text(encoding="utf-8"))
nodes = list(source.iter())
for slot_number, slot in enumerate(slots):
    try:
        node = nodes[slot["node"]]
    except IndexError as error:
        raise RuntimeError(f"Source slot {slot_number} node index is invalid") from error
    if E.QName(node).localname != slot["tag"] or node.get("id") != slot.get("id"):
        raise RuntimeError(f"Source slot {slot_number} node identity drift")
    field = slot["field"]
    actual = node.get(field[1:]) if field.startswith("@") else getattr(node, field)
    if actual is None or actual.strip() != slot["source"]:
        raise RuntimeError(f"Source slot {slot_number} text drift")

records: list[dict] = []
for track_number, track in enumerate(TRACKS):
    target = deepcopy(source)
    target_nodes = list(target.iter())
    for slot_number, slot in enumerate(slots):
        source_text = slot["source"]
        if slot_number in SPECIAL:
            translated = SPECIAL[slot_number][track_number]
        elif source_text in COMMON:
            translated = COMMON[source_text][track_number]
        elif re.fullmatch("[abxlwymnpqz]", source_text):
            translated = source_text
        else:
            raise RuntimeError(f"Missing {track} translation for slot {slot_number}: {source_text!r}")
        node = target_nodes[slot["node"]]
        field = slot["field"]
        if field.startswith("@"):
            node.set(field[1:], translated)
        else:
            original = getattr(node, field)
            prefix = original[: len(original) - len(original.lstrip())]
            suffix = original[len(original.rstrip()) :]
            setattr(node, field, prefix + translated + suffix)
        records.append(
            {
                "track": track,
                "slot": slot_number,
                "node_index": slot["node"],
                "source_id": slot.get("id"),
                "tag": slot["tag"],
                "field": field,
                "source": source_text,
                "target": translated,
            }
        )
    target.set("{http://www.w3.org/XML/1998/namespace}lang", "jv-Latn-ID")
    for image in target.xpath('//*[local-name()="media"]/*[local-name()="image"]'):
        image.set("src", "../assets/canonical/" + Path(image.get("src")).name)
    # Correct mismatched source quotation punctuation only in the Javanese target.
    quoted = target.xpath('(//*[@id="eip-470"]//*[local-name()="math"])[3]')
    if len(quoted) != 1 or quoted[0].tail not in {'."', ' ."'}:
        raise RuntimeError("Expected eip-470 source punctuation was not found")
    quoted[0].tail = "”."
    atomic_bytes(
        ROOT / "translation" / f"{track}.cnxml",
        E.tostring(target, encoding="utf-8", xml_declaration=True),
    )

pivot_bytes = (ROOT / "source/id-pivot.cnxml").read_bytes()
if sha256_bytes(pivot_bytes) != EXPECTED_PIVOT_SHA256:
    raise RuntimeError("Frozen Indonesian comparison section hash mismatch")
id_target = E.fromstring(pivot_bytes)
id_nodes = list(id_target.iter())
if len(id_nodes) != len(nodes):
    raise RuntimeError("Indonesian pivot structure no longer matches the frozen English witness")

# Retain the pinned v1.0.2 Indonesian subtree as the bridge, but replace the
# bounded slots whose source defects, operand order, accessibility descriptions,
# or local register wording were independently resolved in this packet.
ID_REVISED_SLOTS = {
    0, 1, 3, 17, 32, 55, 56, 60, 61, 69, 73, 74, 75, 76, 79, 85,
    91, 92, 93, 95, 98, 99, 100, 101, 102, 104, 105, 106, 107, 108,
    109, 111, 112, 113, 114, 115, 117, 119,
    129, 141, 151, 160, 167, 168, 170, 172, 174, 176, 177, 178,
    181, 183, 184, 186, 187, 189, 191, 193, 195, 196, 197, 198,
    199, 200, 202, 203, 205,
}
id_revisions = []
for slot_number in sorted(ID_REVISED_SLOTS):
    slot = slots[slot_number]
    node = id_nodes[slot["node"]]
    if E.QName(node).localname != slot["tag"] or node.get("id") != slot.get("id"):
        raise RuntimeError(f"Indonesian slot {slot_number} node identity drift")
    source_text = slot["source"]
    if slot_number in SPECIAL:
        translated = SPECIAL[slot_number][2]
    elif source_text in COMMON:
        translated = COMMON[source_text][2]
    elif re.fullmatch("[abxlwymnpqz]", source_text):
        translated = source_text
    else:
        raise RuntimeError(f"Missing Indonesian revision for slot {slot_number}: {source_text!r}")
    field = slot["field"]
    before = node.get(field[1:]) if field.startswith("@") else getattr(node, field)
    if before is None:
        raise RuntimeError(f"Indonesian slot {slot_number} has no {field}")
    if field.startswith("@"):
        node.set(field[1:], translated)
    else:
        prefix = before[: len(before) - len(before.lstrip())]
        suffix = before[len(before.rstrip()) :]
        setattr(node, field, prefix + translated + suffix)
    id_revisions.append(
        {
            "slot": slot_number,
            "node_index": slot["node"],
            "source_id": slot.get("id"),
            "field": field,
            "pivot_text": before.strip() if not field.startswith("@") else before,
            "revised_text": translated,
            "reason": "bounded semantics, source-correction, register, or accessibility reconciliation",
        }
    )
for image in id_target.xpath('//*[local-name()="media"]/*[local-name()="image"]'):
    image.set("src", "../assets/canonical/" + Path(image.get("src")).name)
id_target.set("{http://www.w3.org/XML/1998/namespace}lang", "id-ID")
atomic_bytes(
    ROOT / "translation/id-academic.cnxml",
    E.tostring(id_target, encoding="utf-8", xml_declaration=True),
)

provenance = {
    "schema": "source-slot-translations-v1",
    "purpose": "translation and accessibility, not training",
    "model": "OpenAI Codex gpt-5.6-sol, Ultra",
    "source_section_sha256": EXPECTED_SOURCE_SHA256,
    "slot_count_per_javanese_track": len(slots),
    "records": records,
    "indonesian_bridge": {
        "source": "source/id-pivot.cnxml",
        "source_sha256": EXPECTED_PIVOT_SHA256,
        "mode": "pinned v1.0.2 subtree retained with bounded source-slot revisions",
        "changes": [
            "root xml:lang normalized to id-ID",
            "bounded source slots reconciled for operand order, source defects, register, and accessibility",
            "three media src paths made packet-local",
        ],
        "revisions": id_revisions,
    },
}
atomic_text(
    ROOT / "provenance/TRANSLATION-SLOTS.json",
    json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
)
print(
    f"Authored and verified {len(slots)} source slots per Javanese track; "
    f"retained the pinned Indonesian bridge with {len(id_revisions)} explicit bounded revisions."
)
