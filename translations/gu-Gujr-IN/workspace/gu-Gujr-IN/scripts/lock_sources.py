"""Record acquired source identity and construct the complete source/module map."""
import csv
import hashlib
import json
import io
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "gu-Gujr-IN"
DL = ROOT / "downloads/gu-Gujr-IN"
NS = {"c": "http://cnx.rice.edu/cnxml", "col": "http://cnx.rice.edu/collxml"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(folder, *args):
    return subprocess.check_output(["git", "-C", str(folder), *args], text=True).strip()


def main():
    provenance = LANG / "provenance"
    notices = LANG / "notices"
    notices.mkdir(exist_ok=True)
    repos = []
    for name, role in [("program", "A00/A10 catalog and AX-1/AX-3 specifications"),
                       ("a00-id", "A00 complete Indonesian translation inputs"),
                       ("a10-id", "A10 release authority"),
                       ("openstax-canonical", "Pinned canonical English collections and all module XML; sparse checkout excludes media")]:
        path = DL / name
        repos.append({"id": name, "role": role, "url": git(path, "remote", "get-url", "origin"),
                      "commit": git(path, "rev-parse", "HEAD"), "tree": git(path, "rev-parse", "HEAD^{tree}"),
                      "shallow": git(path, "rev-parse", "--is-shallow-repository") == "true",
                      "local_path": path.relative_to(ROOT).as_posix()})
    small = [
        (DL / "a00-id/LICENSE", notices / "A00-LICENSE.txt"),
        (DL / "a00-id/README.md", notices / "A00-README.md"),
        (DL / "a10-release/source/NOTICE.txt", notices / "A10-NOTICE.txt"),
        (DL / "a10-id/LICENSE", notices / "A10-LICENSE.txt"),
        (DL / "a10-id/README.md", notices / "A10-README.md"),
        (DL / "openstax-canonical/README.md", notices / "OpenStax-README.md"),
        (DL / "openstax-canonical/LICENSE", notices / "OpenStax-LICENSE.txt"),
        (DL / "program/README.md", notices / "program-README.md"),
        (DL / "a00-id/provenance/logbook/authority/prealgebra2e/prealgebra2e-source-manifest.tsv", provenance / "A00-canonical-manifest.tsv"),
        (DL / "a10-release/source/authority/SOURCE_AUTHORITY_MANIFEST.csv", provenance / "A10-canonical-manifest.csv"),
    ]
    retained = []
    for src, dst in small:
        shutil.copyfile(src, dst)
        retained.append({"source": src.relative_to(ROOT).as_posix(), "retained": dst.relative_to(LANG).as_posix(), "sha256": digest(dst)})
    specdir = DL / "program/backend/v2.1/planning/educational-access"
    specs = []
    for file, field, wanted in [("curriculum_portfolios.jsonl", "portfolio_id", ["AX-1", "AX-3"]),
                               ("accessibility_derivatives.jsonl", "derivative_id", ["AX-HTML", "AX-PDF", "AX-OFFLINE", "AX-PLAIN"])]:
        path = specdir / file
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        specs.append({"source": path.relative_to(ROOT).as_posix(), "sha256": digest(path),
                      "records": [r for r in records if r[field] in wanted]})
    (provenance / "AX-specifications.json").write_text(json.dumps(specs, indent=2) + "\n", encoding="utf-8")
    rows = []
    canonical = DL / "openstax-canonical"
    module_ids = []
    coverage_file = LANG/'COVERAGE.json'
    coverage = {(r['program'],r['module_id']):r for r in json.loads(coverage_file.read_text(encoding='utf-8'))['modules']} if coverage_file.is_file() else {}
    queue_file = LANG/'WORK_QUEUE.json'
    drafting = {module for worker in json.loads(queue_file.read_text(encoding='utf-8'))['workers'].values() for module in worker.get('source_modules',[])} if queue_file.is_file() else set()
    for book in ("prealgebra", "elementary-algebra"):
        module_ids += [m.get("document") for m in ET.parse(canonical / f"collections/{book}-2e.collection.xml").findall(".//col:module", NS)]
    # Read Git blobs, not Windows CRLF-converted checkout bytes.
    query = "".join(f"HEAD:modules/{mid}/index.cnxml\n" for mid in module_ids).encode()
    batch = io.BytesIO(subprocess.check_output(["git", "-C", str(canonical), "cat-file", "--batch"], input=query))
    blobs = {}
    for mid in module_ids:
        header = batch.readline().split(); assert header[1] == b"blob"
        blobs[mid] = batch.read(int(header[2])); assert batch.read(1) == b"\n"
    for code, book in [("A00", "prealgebra"), ("A10", "elementary-algebra")]:
        collection = DL / f"openstax-canonical/collections/{book}-2e.collection.xml"
        for order, module in enumerate(ET.parse(collection).findall(".//col:module", NS), 1):
            mid = module.get("document")
            english = DL / f"openstax-canonical/modules/{mid}/index.cnxml"
            frozen = (DL / f"a00-id/provenance/logbook/authority/prealgebra2e/{mid}.source.cnxml" if code == "A00"
                      else DL / f"a10-release/source/authority/source/modules/{mid}/index.cnxml")
            target = (DL / f"a00-id/modules/{mid}/index.cnxml" if code == "A00"
                      else DL / f"a10-release/source/translated/modules/{mid}/index.cnxml")
            assert english.exists() and frozen.exists() and target.exists(), (code, mid)
            exact_hash = hashlib.sha256(blobs[mid]).hexdigest()
            assert exact_hash == digest(frozen), ("canonical mismatch", mid)
            current = coverage.get((code,mid),{})
            status = current.get('source_translation','not_started')
            if status == 'not_started': status = 'assigned_not_started'
            if status == 'assigned_not_started' and code+':'+mid in drafting: status = 'drafting'
            rows.append({"program": code, "order": order, "module_id": mid,
                         "source_title": ET.parse(english).findtext("c:title", namespaces=NS),
                         "canonical_sha256": exact_hash, "indonesian_sha256": digest(target),
                         "canonical_hash_basis": "pinned_git_blob_matches_authority_bytes",
                         "authority_path": frozen.relative_to(ROOT).as_posix(),
                         "canonical_path": english.relative_to(ROOT).as_posix(),
                         "indonesian_path": target.relative_to(ROOT).as_posix(), "status": status})
    with (LANG / "source-module-map.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    assets = []
    for path in sorted(provenance.glob("*-assets.json")):
        assets.extend(json.loads(path.read_text()))
    lock = {"schema": "gujarati-translation-sources-v1", "date": "2026-08-30", "locale": "gu-Gujr-IN",
            "purpose": "translation inputs only; not training or fine-tuning", "repositories": repos,
            "release_assets": assets, "canonical_module_count": len(rows),
            "full_canonical_archive": json.loads((provenance / 'canonical-archive.json').read_text()),
            "canonical_verification": "All 75 A00 and 82 A10 canonical Git-blob hashes match the edition authority copies; Windows checkout newline conversion is excluded from byte comparisons.",
            "retained_notices_and_manifests": retained,
            "limitations": ["The Git checkout is sparse; use the separately acquired and extracted full canonical archive for media. It includes all canonical media.",
                            "Published reader PDFs and duplicate backend archives were not acquired; the complete editable A00/A10 source packages were acquired."]}
    (LANG / "sources.lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(f"Locked {len(repos)} repositories, {len(rows)} verified source/Indonesian modules and {len(assets)} assets.")


if __name__ == "__main__":
    main()
