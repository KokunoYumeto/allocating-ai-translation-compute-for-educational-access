"""Recover only the pinned Indian Bengali A10 preface and its four assets.

Input paths are supplied at runtime; private machine paths are not serialized.
Run once, then use the fully offline build.py for reproducible continuation.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHA = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_json(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", type=Path, required=True)
    ap.add_argument("--prior", type=Path, required=True)
    ap.add_argument("--canonroot", type=Path, required=True)
    args = ap.parse_args()
    lane = args.intake / "bn-Beng-IN/workspace/languages/bn-Beng-IN"
    lock_path = lane / "sources.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8-sig"))
    collection = next(x for x in lock["collections"] if x["course"] == "A10")
    canonical = next(x for x in lock["repositories"] if x["id"] == "upstream-A00-A20")
    comparison = next(x for x in lock["repositories"] if x["id"] == "A10")
    assert canonical["commit"] == "38cae454e644abf9f0a623e876994553881597c9"
    assert collection["collection_modules"] == 82
    source_record = next(x for x in collection["source_modules"] if x["module"] == "m82630")
    next_record = collection["source_modules"][1]
    assert next_record["module"] == "m82451"
    source = args.prior / "source/m82630.en.cnxml"
    assert SHA(source) == source_record["sha256"]
    assert source.stat().st_size == source_record["bytes"]
    (ROOT / "source").mkdir(exist_ok=True)
    shutil.copyfile(source, ROOT / "source/m82630.en.cnxml")
    collection_file = args.prior / "source/collection.xml"
    assert SHA(collection_file) == collection["collection_sha256"]
    shutil.copyfile(collection_file, ROOT / "source/collection.xml")
    manifest_path = args.intake / "EXPORT_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    translation_rows = [x for x in manifest["files"] if x["lane"] == "bn-Beng-IN" and "/translations/" in x["path"].removeprefix("bn-Beng-IN/")]
    module_ids = {x["module"] for x in collection["source_modules"]}
    found = [x for x in translation_rows if any(mid in Path(x["path"]).name for mid in module_ids)]
    assert not found, "Unexpected existing A10 draft: reconcile before writing"
    progress_path = lane / "progress.json"
    progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
    progress_rows = [x for x in progress["modules"] if x["course"] == "A10"]
    assert len(progress_rows) == 82
    assert not any(x["complete"] for x in progress_rows)
    assert all(b["status"] == "pending" for x in progress_rows for b in x["blocks"])
    prior_manifest = json.loads((args.prior / "MANIFEST.json").read_text(encoding="utf-8"))
    assets = []
    (ROOT / "media").mkdir(exist_ok=True)
    for name in ["tryit.png", "howtoicon.png", "media.png", "CNX_ElemAlg_Figure_05_01_015_img.jpg"]:
        prior_path = "assets/a10/" + name
        record = next(x for x in prior_manifest["files"] if x["path"] == prior_path)
        source_asset = args.prior / prior_path
        assert SHA(source_asset) == record["sha256"]
        assert source_asset.stat().st_size == record["bytes"]
        shutil.copyfile(source_asset, ROOT / "media" / name)
        assets.append({"path": "media/" + name, "sha256": record["sha256"], "bytes": record["bytes"], "role": "unchanged canonical media witness"})
    license_path = args.prior / "LICENSE.txt"
    assert SHA(license_path) == "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"
    shutil.copyfile(license_path, ROOT / "LICENSE.txt")
    canon_lock = json.loads((lane / "canon/references.lock.json").read_text(encoding="utf-8"))
    witness = next(x for x in canon_lock["sources"] if x["id"] == "WB-Class7-Learning-Bridge")
    consulted = []
    for p in [x for x in witness["read_pages"] if x["pdf_page"] in [189, 226]]:
        evidence = {"pdf_page": p["pdf_page"]}
        for kind in ["ocr", "render"]:
            file = args.canonroot / "WB-Class7-Learning-Bridge" / Path(p[kind]["path"]).name
            assert SHA(file) == p[kind]["sha256"]
            evidence[kind] = {"sha256": SHA(file), "bytes": file.stat().st_size, "filename": file.name}
        consulted.append(evidence)
    write_json("SOURCE_RECOVERY.json", {
        "schema": "a10.bn-Beng-IN.source-recovery.v1", "locale": "bn-Beng-IN", "module": "m82630",
        "authority": {"repository": canonical["url"].removesuffix(".git"), "commit": canonical["commit"], "collection": "col31130", "collection_uuid": collection["collection_id"], "collection_sha256": collection["collection_sha256"], "collection_module_count": 82},
        "source": {"path": "source/m82630.en.cnxml", "sha256": SHA(source), "bytes": source.stat().st_size, "official_relative_path": "modules/m82630/index.cnxml", "recovery": "Byte-identical reuse from verified A10 Shahmukhi checkpoint; independently matched Indian Bengali source lock."},
        "indonesian_comparison": {"repository": comparison["url"].removesuffix(".git"), "commit": comparison["commit"], "release": "v1.0.2", "use_in_this_packet": "Pin preserved as comparison identity; preface translated from canonical English, not claimed freshly compared against Indonesian bytes."},
        "recovered_lane_evidence": {"export_manifest_sha256": SHA(manifest_path), "source_lock_sha256": SHA(lock_path), "progress_sha256": SHA(progress_path), "terminology_sha256": SHA(lane / "terminology.tsv"), "canon_readme_sha256": SHA(lane / "canon/README.md"), "translation_inventory_rows": len(translation_rows), "a10_draft_matches": [], "a10_modules_in_progress": 82, "a10_complete_modules": 0, "a10_block_statuses": ["pending"], "finding": "No A10 draft found in recovered translation inventory; all 82 A10 progress records are explicitly pending. Acquisition is not translation credit."},
        "media": assets,
        "canon": {"id": witness["id"], "url": witness["url"], "pdf_sha256": witness["sha256"], "scope": "West Bengal government Pathan Setu, Class VII (2021), printed pages 10 and 47; language witnesses only, not mathematical source authority or curriculum certification.", "read_actual_ocr_and_images": consulted, "redistributed_reference_content": False},
        "next_module": {"module": next_record["module"], "source_sha256": next_record["sha256"], "source_title": next_record["title"]}
    })
    print("Pinned preface, collection, four media and license recovered; A10 draft absence checked against inventory plus 82 progress rows.")


if __name__ == "__main__":
    main()
