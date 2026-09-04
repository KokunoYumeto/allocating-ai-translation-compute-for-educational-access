"""Capture acquired source identities and native module order; no audits/network."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "vi-Latn-VN"
D = ROOT / "downloads"
NS = {"c": "http://cnx.rice.edu/collxml", "m": "http://cnx.rice.edu/mdml", "x": "http://cnx.rice.edu/cnxml"}


def digest(path):
    with path.open("rb") as stream:
        h = sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True, encoding="utf-8").strip()


def modules(collection):
    return [n.get("document") for n in ET.parse(collection).findall(".//c:module", NS)]


def main():
    definitions = [
        ("catalog", "program-matematika-indonesia", "2f0e52280791854f904475e5f92392f52745ea24", None),
        ("A30-id", "openstax-precalculus-2e-id", "3209a5a2dea18c2fc527c5ea41b7dd2195076e40", None),
        ("B20-id", "clp1-differential-calculus-id", "59aaa2a6145eecd67680752c28ad4be7e43eff5e", ["latex", "pretext", "provenance", "scripts"]),
        ("B40-id", "hefferon-linear-algebra-id", "e84ce2956a7304830c42eba70106f940fefee7c4", ["00_control", "authority", "publication", "source", "tools"]),
        ("B60-id", "clp4-vector-calculus-id", "3abfd2deb01e8ea005da8450ac3a2228410468d9", None),
        ("B80-id-canonical", "mathematical-computing-reproducible-experiments-id", "403e93a6d8bdadbcd42385981bbe4b39577ca069", ["00_control", "source", "scripts", "tests", "environment", "build-support"]),
        ("A30-upstream", "upstream-openstax", "789b54099106b071d1d32bfcee454fed72eb4768", ["collections", "media"]),
        ("B20-upstream", "upstream-clp1", "9f0295936d395bec68dab7915057135a2c7f0414", ["latex", "pretext"]),
        ("B60-upstream", "upstream-clp4", "6743bab1648c442c4efdf06f4b05be1bfc83db72", ["latex", "pretext"]),
    ]
    precalc_ids = modules(D / "upstream-openstax/collections/precalculus-2e.collection.xml")
    inventories = []
    repos = []
    for identity, name, pin, sparse in definitions:
        path = D / name
        assert git(path, "rev-parse", "HEAD") == pin, identity
        if identity == "A30-upstream":
            sparse += [f"modules/{m}" for m in precalc_ids]
        present = []
        # Inventory checkout files, excluding .git. Source Git commit is byte authority;
        # observed SHA256 values can also reflect the host's checkout newline settings.
        for relative in git(path, "ls-files").splitlines():
            file = path / relative
            if file.is_file():
                present.append(file)
                if identity != "catalog":
                    inventories.append([identity, file.relative_to(ROOT).as_posix(), file.stat().st_size, digest(file)])
        repos.append({"id": identity, "url": git(path, "remote", "get-url", "origin"), "commit": pin,
                      "tree": git(path, "rev-parse", "HEAD^{tree}"), "local_path": path.relative_to(ROOT).as_posix(),
                      "acquisition": "shallow pinned checkout", "sparse_paths": sparse,
                      "materialized_files": len(present), "materialized_bytes": sum(p.stat().st_size for p in present)})
    archives = [
        ("A30-id-source", "a30-edition/source-core.zip", "https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.58-reader.1/precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip", "9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca", "a30-edition/source-core"),
        ("B60-id-source", "clp4-vector-calculus-id/CLP-4-Kalkulus-Vektor-Bahasa-Indonesia-sumber-backend.zip", None, "3f58f4762b1b638a051afc3c1f66c2bd9ae87a5ef3e445902abe2a8235f64b95", "clp4-edition"),
        ("B40-upstream", "hefferon-linear-algebra-id/authority/archives/linear-algebra-df2262e089a02651c127f1dd12649c4622ee1383.zip", "https://gitlab.com/jim.hefferon/linear-algebra/-/archive/df2262e089a02651c127f1dd12649c4622ee1383/linear-algebra-df2262e089a02651c127f1dd12649c4622ee1383.zip", "b409fc82a8323578e71d8095b9ab4bc9ca814d5a0d9cc6d125dd6b4d81dc23d0", "upstream-hefferon"),
    ]
    archive_records = []
    for identity, relative, url, expected, extracted in archives:
        path = D / relative
        assert digest(path) == expected, identity
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, identity
            members = [n for n in archive.infolist() if not n.is_dir()]
        archive_records.append({"id": identity, "path": path.relative_to(ROOT).as_posix(), "url": url,
                                "sha256": expected, "bytes": path.stat().st_size, "files": len(members),
                                "uncompressed_bytes": sum(n.file_size for n in members), "crc": "pass",
                                "extracted_path": f"downloads/{extracted}",
                                "retrieval": "release asset" if identity == "A30-id-source" else "embedded in pinned Indonesian repository",
                                "upstream_commit": "df2262e089a02651c127f1dd12649c4622ee1383" if identity == "B40-upstream" else None})
    with (LANG / "provenance/acquired-files.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["source_id", "local_path", "bytes", "observed_sha256"])
        writer.writerows(sorted(inventories))
    js = (D / "program-matematika-indonesia/docs/courses.js").read_text(encoding="utf-8")
    courses = json.loads(js.split("Object.freeze(", 1)[1].split(");", 1)[0])
    selected = [c for c in courses if c["id"] in ["A30", "B20", "B40", "B60", "B80", "A20", "B10", "B30", "B50"]]
    dump(LANG / "provenance/catalog-selection.json", selected)
    for origin, target in [
        ("openstax-precalculus-2e-id/RELEASE_MANIFEST.json", "A30-release.json"),
        ("clp4-vector-calculus-id/RELEASE_MANIFEST.json", "B60-release.json"),
        ("hefferon-linear-algebra-id/publication/release-manifest.json", "B40-release.json"),
        ("mathematical-computing-reproducible-experiments-id/00_control/SOURCE_SELECTION.md", "B80-source-selection.md"),
        ("a30-edition/source-core/00_control/AUTHORITY_RECEIPT.json", "A30-authority.json"),
    ]:
        shutil.copyfile(D / origin, LANG / "provenance" / target)
    pilot_names = {Path(n.get("src")).name for n in ET.parse(LANG / "sources/m49301-pilot-source.cnxml").findall(".//x:image", NS)}
    with (D / "a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv").open(encoding="utf-8-sig", newline="") as stream:
        assets = [r for r in csv.DictReader(stream) if Path(r["asset_path"]).name in pilot_names]
    assert len(assets) == 4 and all(a["admission"] == "admitted" for a in assets)
    for asset in assets:
        assert digest(LANG / "assets" / Path(asset["asset_path"]).name) == asset["sha256"]
    dump(LANG / "provenance/pilot-asset-notices.json", assets)
    language_sources = [
        {"id": "C-VI-01", "url": "https://fami.hust.edu.vn/wp-content/uploads/Giai-tich-1.pdf", "path": "downloads/vi-canon/hust-giai-tich-1.pdf", "role": "language witness only; not content donor", "ocr_pdf_pages": [7, 8, 9, 10]},
        {"id": "C-VI-02", "url": "https://www.daisotuyentinh.com/2023/08/anh-xa-tuyen-tinh_21.html", "path": "downloads/vi-canon/linear-map.html", "role": "language witness only; literal LaTeX in HTML"},
    ]
    for record in language_sources:
        file = ROOT / record["path"]
        record.update({"sha256": digest(file), "bytes": file.stat().st_size})
    lock = {"schema_version": 1, "locale": "vi-Latn-VN", "observed_date": "2026-08-30",
            "purpose": "translation inputs only, not training/fine-tuning data", "repositories": repos, "archives": archive_records,
            "language_canon": language_sources, "file_inventory": "provenance/acquired-files.csv",
            "file_inventory_sha256": digest(LANG / "provenance/acquired-files.csv"),
            "B80_authority": "Original Indonesian 14-unit coursebook at B80-id-canonical; comparison-only donors excluded",
            "checkout_note": "Sparse checkouts exclude some generated readers/backends. Commit/tree pins are canonical; inventory SHA256 values are observed checkout bytes. A30 includes whole bundle media, but only its selected 87 prose modules.",
            "A30_owner_release": "0.1.0-alpha.58-reader.1; 58/87 modules; catalog descriptive summary is stale",
            "no_external_publication": True}
    dump(LANG / "sources.lock.json", lock)
    unit_rows = []
    for order, identity in enumerate(precalc_ids, 1):
        path = D / f"upstream-openstax/modules/{identity}/index.cnxml"
        title = ET.parse(path).getroot().find("x:title", NS).text
        unit_rows.append({"course": "A30", "order": order, "source_id": identity, "title_en": title,
                          "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                          "status_vi": "partial translation; see STATUS.json for completed units" if identity == "m49301" else "not translated"})
    mains = [
        ("B20", D / "clp1-differential-calculus-id/latex/textbook/clp_1_dc_text.tex", "input"),
        ("B40", D / "hefferon-linear-algebra-id/source/linear-algebra/src/book.tex", "include"),
        ("B60", D / "clp4-edition/clp4-vector-calculus-id/repo/latex/textbook/clp_4_vc_text.tex", "input"),
    ]
    for course, mainfile, directive in mains:
        text = re.sub(r"(?m)%.*$", "", mainfile.read_text(encoding="utf-8")).split(r"\mainmatter", 1)[1]
        for order, value in enumerate(re.findall(r"\\" + directive + r"\{([^}]+)\}", text), 1):
            path = mainfile.parent / (value + ".tex")
            assert path.exists(), path
            unit_rows.append({"course": course, "order": order, "source_id": value, "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "status_vi": "not translated", "order_kind": "native main-file include order; includes appendices/topics"})
    quarto = (D / "mathematical-computing-reproducible-experiments-id/_quarto.yml").read_text(encoding="utf-8")
    for order, name in enumerate(re.findall(r"^    - (source/units/[^\n]+\.qmd)$", quarto, re.M), 1):
        path = D / "mathematical-computing-reproducible-experiments-id" / name
        unit_rows.append({"course": "B80", "order": order, "source_id": path.stem, "path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "status_vi": "not translated"})
    algebra_ids = modules(D / "upstream-openstax/collections/algebra-and-trigonometry-2e.collection.xml")
    portfolios = [json.loads(line) for line in (D / "program-matematika-indonesia/backend/v2.1/planning/educational-access/curriculum_portfolios.jsonl").read_text(encoding="utf-8").splitlines()]
    map_data = {"locale": "vi-Latn-VN", "courses": [{"id": c["id"], "prerequisites": c["prerequisites"], "assigned": c["id"] in ["A30", "B20", "B40", "B60", "B80"]} for c in selected],
                "native_source_units": unit_rows, "sequence_note": "Native reading order is not an assertion that every appendix/topic is a hard prerequisite.",
                "portfolio_authority": [p for p in portfolios if p["portfolio_id"] in ["MV-1", "SB-1"]],
                "MV-1_identity_crosswalk": {"basis": "exact document IDs in collections at the same OpenStax pin, not inferred title equivalence", "precalculus_count": len(precalc_ids), "algebra_trigonometry_count": len(algebra_ids),
                                           "shared_module_ids": sorted(set(precalc_ids) & set(algebra_ids)), "MV-1_not_in_A30": [m for m in algebra_ids if m not in precalc_ids], "A30_not_in_MV-1": [m for m in precalc_ids if m not in algebra_ids]},
                "SB-1_gap": "MV-1 plus Introductory Statistics 2e. Statistics is not assigned/acquired/translated here; no completion or equivalence claimed.",
                "next_translation": json.loads((LANG / "STATUS.json").read_text(encoding="utf-8"))["next"]}
    dump(LANG / "module-map.json", map_data)
    print(json.dumps({"repositories": len(repos), "archives": len(archives), "inventory_files": len(inventories), "native_units": len(unit_rows), "A30_modules": len(precalc_ids), "MV1_shared": len(set(precalc_ids) & set(algebra_ids))}))


if __name__ == "__main__":
    main()
