"""Record the acquired translation inputs and preserve small provenance witnesses.
Run once after acquisition; review any later lockfile change. This is not a corpus exporter.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
UPSTREAM = ROOT / f"downloads/osbooks-prealgebra-bundle-{COMMIT}"
NS = {"c": "http://cnx.rice.edu/cnxml", "col": "http://cnx.rice.edu/collxml"}

def digest(path):
    return hashlib.file_digest(path.open("rb"), "sha256").hexdigest()

def witness(source, destination):
    target = LANG / "provenance" / destination
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    return {"path": target.relative_to(ROOT).as_posix(), "sha256": digest(target)}

def main():
    repositories = []
    for role, folder in [("catalog", "program-matematika-indonesia"), ("allocation", "allocation-reference"), ("A00", "openstax-prealgebra-2e-id-ID"), ("A10", "openstax-elementary-algebra-2e-id"), ("A20", "openstax-intermediate-algebra-2e-id")]:
        path = ROOT / "downloads" / folder
        def git(*args):
            return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()
        repositories.append({"role": role, "path": path.relative_to(ROOT).as_posix(), "url": git("remote", "get-url", "origin"), "commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"), "shallow": git("rev-parse", "--is-shallow-repository") == "true"})
    artifacts = []
    assets = [
        ("A10", "downloads/release-assets/A10/elementary-algebra-2e-id-ID-1.0.2-source.zip", "https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/elementary-algebra-2e-id-ID-1.0.2-source.zip", "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456"),
        ("A20", "downloads/release-assets/A20/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip", "https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.3.0-wip/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip", "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
        ("canonical-A00-A10-A20", "downloads/osbooks-prealgebra-bundle-pinned.zip", f"https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/{COMMIT}", None),
        ("Tamil-register-reference", "downloads/tamil-canon/tn-scert-6-term1-maths-2018.pdf", "https://www.kulikaraighss.in/books/6t1all/6t1maths.pdf", None),
        ("OCR-dependency-not-translation-material", "downloads/tessdata/tam.traineddata", "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/tam.traineddata", None),
        ("font", "ta-Taml-IN/assets/fonts/NotoSansTamil.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstamil/NotoSansTamil%5Bwdth,wght%5D.ttf", None),
        ("font-license", "ta-Taml-IN/assets/fonts/OFL.txt", "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstamil/OFL.txt", None),
    ]
    for role, local, url, expected in assets:
        path = ROOT / local
        actual = digest(path)
        assert not expected or actual == expected, (local, actual, expected)
        artifacts.append({"role": role, "path": local, "url": url, "bytes": path.stat().st_size, "sha256": actual, "publisher_sha256": expected, "hash_basis": "publisher checksum matched" if expected else "local acquisition hash; URL/commit recorded"})
    witnesses = []
    for source, dest in [
        (ROOT / "downloads/openstax-prealgebra-2e-id-ID/LICENSE", "A00-LICENSE.txt"),
        (ROOT / "downloads/openstax-prealgebra-2e-id-ID/README.md", "A00-README.md"),
        (ROOT / "downloads/openstax-prealgebra-2e-id-ID/modules/m81243/index.cnxml", "m81243.id-ID.cnxml"),
        (UPSTREAM / "modules/m81243/index.cnxml", "m81243.en.cnxml"),
        (UPSTREAM / "modules/m81241/index.cnxml", "A00-preface-credits.en.cnxml"),
        (UPSTREAM / "collections/prealgebra-2e.collection.xml", "prealgebra-2e.collection.xml"),
        (UPSTREAM / "collections/elementary-algebra-2e.collection.xml", "elementary-algebra-2e.collection.xml"),
        (UPSTREAM / "collections/intermediate-algebra-2e.collection.xml", "intermediate-algebra-2e.collection.xml"),
        (ROOT / "downloads/openstax-elementary-algebra-2e-id/SOURCE_AUTHORITY.md", "A10-SOURCE_AUTHORITY.md"),
        (ROOT / "downloads/A10-source/NOTICE.txt", "A10-NOTICE.txt"),
        (ROOT / "downloads/A10-source/LICENSE.txt", "A10-LICENSE.txt"),
        (ROOT / "downloads/A20-source/LICENSE.txt", "A20-LICENSE.txt"),
        (ROOT / "downloads/openstax-intermediate-algebra-2e-id/RELEASE_MANIFEST.json", "A20-repository-stale-v0.1.3-manifest.json"),
        (ROOT / "downloads/release-assets/A10/elementary-algebra-2e-id-ID-1.0.2-release-manifest.json", "A10-v1.0.2-release-manifest.json"),
        (ROOT / "downloads/release-assets/A20/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-release-manifest.json", "A20-v0.3.0-wip-release-manifest.json"),
        (ROOT / "downloads/release-assets/A20/SHA256SUMS.txt", "A20-v0.3.0-wip-SHA256SUMS.txt"),
        (ROOT / "downloads/allocation-reference/curriculum_portfolios.csv", "curriculum_portfolios.csv"),
        (ROOT / "downloads/program-matematika-indonesia/backend/v2.1/planning/educational-access/curriculum_portfolios.jsonl", "catalog-accessibility-portfolios.jsonl"),
    ]:
        witnesses.append(witness(source, dest))
    collections = []
    for role, name, count in [("A00", "prealgebra", 75), ("A10", "elementary-algebra", 82), ("A20", "intermediate-algebra", 83)]:
        file = UPSTREAM / f"collections/{name}-2e.collection.xml"
        modules = [n.get("document") for n in ET.parse(file).findall(".//col:module", NS)]
        assert len(modules) == count
        assert all((UPSTREAM / f"modules/{m}/index.cnxml").is_file() for m in modules)
        collections.append({"role": role, "collection": file.name, "references": len(modules), "all_module_sources_present": True, "sha256": digest(file)})
    for p in [ROOT / assets[i][1] for i in range(3)]:
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
    lock = {
        "schema": "translation-input-lock/v1", "locale": "ta-Taml-IN", "acquired_on": "2026-08-30", "purpose": "translation inputs and register references; not model training/fine-tuning data",
        "repositories": repositories, "artifacts": artifacts,
        "canonical": {"repository": "https://github.com/openstax/osbooks-prealgebra-bundle", "commit": COMMIT, "tree": "7907e4c81d43de1c3b6da173f0eb273c01dc5b55", "extracted_path": UPSTREAM.relative_to(ROOT).as_posix(), "acquisition": "pinned archive; partial Git checkout failed and is not used", "collections": collections},
        "edition_coverage": {"A00": "v0.2.7: 75/75 references", "A10": "v1.0.2: 82/82 modules", "A20": "v0.3.0-wip release assets: 48/83 through m81441; root README/manifest remain older"},
        "AX-1_AX-3": {"kind": "cross-project derivative specifications, not independent repositories", "repository_roles": ["allocation", "catalog"], "authority_witness": "provenance/catalog-accessibility-portfolios.jsonl"},
        "witnesses": witnesses,
        "excluded_from_acquisition": "Large reader PDFs/backend archives are not needed as translation inputs where editable source and media are acquired. No claim to have downloaded those optional redundant payloads.",
    }
    (LANG / "sources.lock.json").write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"repositories": len(repositories), "artifacts": len(artifacts), "witnesses": len(witnesses), "collections": collections}, indent=2))

if __name__ == "__main__":
    main()
