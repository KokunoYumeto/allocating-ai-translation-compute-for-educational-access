"""Prepare PNB-009's unchanged JPEGs and exact existing component notices.

Validate all declarations and existing destinations before creating anything.
Never overwrite a differing file; no download, rights re-audit or source edits.
"""
from pathlib import Path, PurePosixPath
import argparse
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / "source-excerpts/manifest-009.json"
EXCERPT = BASE / "source-excerpts/unit-009.cnxml"
CANONICAL = ROOT / "downloads/upstream/osbooks-college-algebra-bundle/modules/m49301/index.cnxml"
SOURCE_ROOT = ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle"
RIGHTS = ROOT / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv"
NOTICE = BASE / "provenance/unit-009-component-notices.json"
SECTION = "fs-id1165137737761"
FIELDS = ["rights_component_id", "asset_path", "bytes", "sha256", "source_modules",
          "classification", "admission", "license_id", "attribution", "required_action"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def signature(node):
    return node.tag, node.attrib, node.text, tuple((signature(c), c.tail) for c in node)


def safe_relative(value):
    path = PurePosixPath(value)
    assert not path.is_absolute() and ".." not in path.parts
    assert "\\" not in value and ":" not in value and path.as_posix() == value
    return path


def validate_selection(source, full, manifest):
    assert source.attrib == {"id": "m49301-unit-009-excerpt"}
    assert [tag(n) for n in source] == [tag(n) for n in full] == ["title", "metadata", "content", "glossary"]
    assert manifest["selection_ids"] == [SECTION] and manifest["next_source_id"] is None
    for selected, original in zip(source, full):
        assert selected.tag == original.tag and selected.tail == original.tail
        if tag(selected) == "content":
            assert selected.attrib == original.attrib and selected.text == original.text
            assert len(selected) == 1 and len(original) == 10
            assert selected[0].get("id") == original[-1].get("id") == SECTION
            assert signature(selected[0]) == signature(original[-1]) and selected[0].tail == original[-1].tail
        else:
            assert signature(selected) == signature(original)
    assert sum(bool(n.get("id")) for n in source.iter()) - 1 == 437


def validate_declared_images(source, specs):
    parent = {c: n for n in source.iter() for c in n}
    media = [n for n in source.iter() if tag(n) == "media"]
    assert len(media) == len(specs) == 26
    assert [n.get("id") for n in media] == [s["media_id"] for s in specs]
    assert all(len({s[key] for s in specs}) == 26 for key in ("media_id", "source_path", "path"))
    owners = []
    for original, spec in zip(media, specs):
        assert len(original) == 1 and tag(original[0]) == "image"
        assert original[0].get("mime-type") == "image/jpg"
        assert original[0].get("src") == "../../" + spec["source_path"]
        assert spec["source_alt"] == original.get("alt")
        source_path, target = safe_relative(spec["source_path"]), safe_relative(spec["path"])
        assert source_path.parts[0] == "media" and len(source_path.parts) == 2
        match = re.fullmatch(r"CNX_Precalc_Figure_(01_01_\d{3})-[a-f0-9]{4}\.jpg", source_path.name)
        assert match and target.as_posix() == "assets/Exercise_" + match[1] + ".jpg"
        assert "figure_id" not in spec and "local_label" not in spec
        assert tag(parent[original]) in ("problem", "solution")
        assert type(spec["width"]) is type(spec["height"]) is int and spec["width"] > 0 and spec["height"] > 0
        owners.append(tag(parent[original]))
    assert owners == ["problem"] * 20 + ["solution"] * 6


def prepare(check_only=False):
    inputs = {p: p.read_bytes() for p in (MANIFEST, EXCERPT, CANONICAL, RIGHTS)}
    manifest = json.loads(inputs[MANIFEST], object_pairs_hook=unique_object)
    assert manifest["unit"] == "PNB-009" and manifest["module"] == "m49301"
    assert manifest["commit"] == "789b54099106b071d1d32bfcee454fed72eb4768"
    assert manifest["source_excerpt"] == EXCERPT.name
    assert digest(inputs[CANONICAL]) == "f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612"
    assert digest(inputs[CANONICAL].replace(b"\r\n", b"\n")) == manifest["full_module_sha256"]
    assert digest(inputs[EXCERPT].replace(b"\r\n", b"\n")) == manifest["excerpt_sha256"]
    source, full = ETree(inputs[EXCERPT]), ETree(inputs[CANONICAL])
    validate_selection(source, full, manifest)
    validate_declared_images(source, manifest["images"])
    rows_reader = csv.DictReader(io.StringIO(inputs[RIGHTS].decode("utf-8-sig"), newline=""))
    rights = list(rows_reader)
    assert rows_reader.fieldnames == FIELDS
    prepared = []
    for spec in manifest["images"]:
        source_path = (SOURCE_ROOT / spec["source_path"]).resolve()
        destination = (BASE / spec["path"]).resolve()
        assert source_path.is_relative_to((SOURCE_ROOT / "media").resolve())
        assert destination.is_relative_to((BASE / "assets").resolve())
        data = source_path.read_bytes()
        assert digest(data) == spec["sha256"]
        assert jpeg_dimensions(data) == (spec["width"], spec["height"])
        matches = [row for row in rights if row["asset_path"] == spec["source_path"]]
        assert len(matches) == 1
        row = matches[0]
        assert row["rights_component_id"] == spec["rights_component_id"]
        assert row["sha256"] == spec["sha256"] and int(row["bytes"]) == len(data)
        assert row["admission"] == "admitted" and row["source_modules"] == "m49301"
        assert not destination.exists() or destination.read_bytes() == data, "Different existing asset; refusing overwrite"
        prepared.append((destination, data, row.copy()))
    notice_bytes = (json.dumps([row for _, _, row in prepared], ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    assert not NOTICE.exists() or NOTICE.read_bytes().replace(b"\r\n", b"\n") == notice_bytes, "Different existing notice; refusing overwrite"
    assert all(path.read_bytes() == data for path, data in inputs.items()), "Inputs changed before output creation"
    result = {"unit": "PNB-009", "images": 26, "image_bytes": sum(len(data) for _, data, _ in prepared),
              "notice_sha256_lf": digest(notice_bytes), "check_only": check_only}
    if check_only:
        return result
    for destination, data, _ in prepared:
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with destination.open("xb") as stream:
                stream.write(data)
        except FileExistsError:
            pass
        assert destination.read_bytes() == data
    NOTICE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with NOTICE.open("xb") as stream:
            stream.write(notice_bytes)
    except FileExistsError:
        pass
    assert NOTICE.read_bytes().replace(b"\r\n", b"\n") == notice_bytes
    return result


def ETree(data):
    return ET.fromstring(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    arguments = parser.parse_args()
    print(json.dumps(prepare(arguments.check_only), sort_keys=True))
