"""Prepare only PNB-008's unchanged images and exact previously audited rows.

All source, declaration, existing-destination and notice checks precede writes.
This carries forward the supplied component decisions; it is not a new audit.
"""
from pathlib import Path, PurePosixPath
import argparse
import csv
import hashlib
import io
import json
import xml.etree.ElementTree as ET

from qa_menu import jpeg_dimensions


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / "source-excerpts/manifest-008.json"
RIGHTS = ROOT / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv"
SOURCE_ROOT = ROOT / "downloads/complete-upstream/osbooks-college-algebra-bundle"
NOTICE = BASE / "provenance/unit-008-component-notices.json"
COMMIT = "789b54099106b071d1d32bfcee454fed72eb4768"
SELECTED = ["fs-id1165135422920", "fs-id1165135435781", "fs-id1165137610952",
            "fs-id1165135545919", "fs-id1165135203679", "fs-id1165137692068"]
FIELDS = ["rights_component_id", "asset_path", "bytes", "sha256", "source_modules",
          "classification", "admission", "license_id", "attribution", "required_action"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def signature(node):
    return (node.tag, dict(node.attrib), node.text,
            tuple((signature(child), child.tail) for child in node))


def safe_relative(value):
    path = PurePosixPath(value)
    assert not path.is_absolute() and ".." not in path.parts
    assert "\\" not in value and ":" not in value
    assert path.as_posix() == value
    return path


def validate_declared_images(source, specs):
    """Bind declarations to all actual media, including the nine table entries."""
    parent = {child: node for node in source.iter() for child in node}
    media = [node for node in source.iter() if tag(node) == "media"]
    assert len(specs) == len(media) == 15
    assert [spec["media_id"] for spec in specs] == [node.get("id") for node in media]
    assert len({spec["media_id"] for spec in specs}) == 15
    assert len({spec["source_path"] for spec in specs}) == 15
    assert len({spec["path"] for spec in specs}) == 15
    figure_count = table_count = 0
    for spec, node in zip(specs, media):
        assert len(node) == 1 and tag(node[0]) == "image"
        assert node[0].get("mime-type") == "image/jpg"
        source_path = safe_relative(spec["source_path"])
        target_path = safe_relative(spec["path"])
        assert source_path.parts[0] == "media" and len(source_path.parts) == 2
        assert target_path.parts[0] == "assets" and len(target_path.parts) == 2
        assert source_path.suffix == target_path.suffix == ".jpg"
        assert node[0].get("src") == "../../" + spec["source_path"]
        owner = parent[node]
        if tag(owner) == "figure":
            figure_count += 1
            assert spec["figure_id"] == owner.get("id")
            assert spec["local_label"] == "1.1." + str(int(owner.get("id").rsplit("_", 1)[1]))
            assert target_path.name == spec["figure_id"] + ".jpg"
        else:
            table_count += 1
            assert tag(owner) == "entry" and list(owner) == [node]
            assert not (owner.text or "").strip() and not (node.tail or "").strip()
            assert "figure_id" not in spec and "local_label" not in spec
            row = parent[owner]
            assert tag(row) == "row" and list(row).index(owner) == 2
            group = parent[row]
            assert tag(group) == "tbody"
            table = parent[parent[group]]
            assert tag(table) == "table" and table.get("id") == "Table_01_01_14"
            assert list(group).index(row) == table_count - 1
            number = source_path.name.split("01_01_", 1)[1][:3]
            assert target_path.name == "Toolkit_01_01_" + number + ".jpg"
        assert isinstance(spec["width"], int) and isinstance(spec["height"], int)
        assert spec["width"] > 0 and spec["height"] > 0
    assert (figure_count, table_count) == (6, 9)


def prepare(check_only=False):
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["unit"] == "PNB-008" and manifest["module"] == "m49301"
    assert manifest["commit"] == COMMIT and manifest["selection_ids"] == SELECTED
    assert manifest["source_excerpt"] == "unit-008.cnxml"
    assert manifest["next_source_id"] == "fs-id1165137737761"
    excerpt = BASE / "source-excerpts" / manifest["source_excerpt"]
    excerpt_bytes = excerpt.read_bytes()
    assert digest(excerpt_bytes.replace(b"\r\n", b"\n")) == manifest["excerpt_sha256"]
    source = ET.fromstring(excerpt_bytes)
    assert [node.get("id") for node in source] == SELECTED

    # Check the same six complete subtrees against the pinned full witness.
    witness_path = ROOT / "downloads/m49301.cnxml"
    witness_bytes = witness_path.read_bytes()
    assert digest(witness_bytes) == manifest["full_module_sha256"]
    full = ET.fromstring(witness_bytes)
    original = [node for node in full.iter() if node.get("id") in SELECTED]
    assert [node.get("id") for node in original] == SELECTED
    assert all(signature(left) == signature(right) and left.tail == right.tail
               for left, right in zip(source, original))
    parent = {child: node for node in full.iter() for child in node}
    content = parent[original[0]]
    assert all(parent[node] is content for node in original)
    assert list(content)[3:9] == original
    assert list(content)[9].get("id") == manifest["next_source_id"]
    validate_declared_images(source, manifest["images"])

    rights_bytes = RIGHTS.read_bytes()
    reader = csv.DictReader(io.StringIO(rights_bytes.decode("utf-8-sig"), newline=""))
    rights = list(reader)
    assert reader.fieldnames == FIELDS, "Unexpected existing rights-row schema"
    source_root = SOURCE_ROOT.resolve()
    asset_root = (BASE / "assets").resolve()
    prepared = []
    for spec in manifest["images"]:
        image_source = (source_root / spec["source_path"]).resolve()
        target = (BASE / spec["path"]).resolve()
        assert image_source.is_relative_to(source_root / "media")
        assert target.is_relative_to(asset_root)
        data = image_source.read_bytes()
        assert digest(data) == spec["sha256"], "Source image digest mismatch"
        assert jpeg_dimensions(data) == (spec["width"], spec["height"])
        matches = [row for row in rights if row["asset_path"] == spec["source_path"]]
        assert len(matches) == 1, "Missing or duplicate retained component row"
        row = matches[0]
        assert row["sha256"] == spec["sha256"] and int(row["bytes"]) == len(data)
        assert row["admission"] == "admitted" and row["source_modules"] == "m49301"
        assert not target.exists() or digest(target.read_bytes()) == spec["sha256"], (
            "Different existing asset; refusing overwrite: " + str(target))
        prepared.append((target, data, row.copy()))

    notice = NOTICE.resolve()
    assert notice.is_relative_to((BASE / "provenance").resolve())
    notice_bytes = (json.dumps([row for _, _, row in prepared], ensure_ascii=False,
                              indent=2) + "\n").encode("utf-8")
    assert not notice.exists() or notice.read_bytes().replace(b"\r\n", b"\n") == notice_bytes, (
        "Different existing component notice; refusing overwrite")
    # Detect a coordinated-input change before any output creation.
    assert MANIFEST.read_bytes() == manifest_bytes and excerpt.read_bytes() == excerpt_bytes
    assert RIGHTS.read_bytes() == rights_bytes and witness_path.read_bytes() == witness_bytes

    result = {"unit": "PNB-008", "images": len(prepared),
              "image_bytes": sum(len(data) for _, data, _ in prepared),
              "notice_sha256_lf": digest(notice_bytes), "check_only": check_only}
    if check_only:
        return result

    # Nothing is overwritten. Exclusive creation also protects a concurrent writer.
    for target, data, row in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("xb") as stream:
                stream.write(data)
        except FileExistsError:
            pass
        assert digest(target.read_bytes()) == row["sha256"]
    notice.parent.mkdir(parents=True, exist_ok=True)
    try:
        with notice.open("xb") as stream:
            stream.write(notice_bytes)
    except FileExistsError:
        pass
    assert notice.read_bytes().replace(b"\r\n", b"\n") == notice_bytes
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="Validate every input and existing output without writing")
    arguments = parser.parse_args()
    print(json.dumps(prepare(check_only=arguments.check_only), sort_keys=True))
