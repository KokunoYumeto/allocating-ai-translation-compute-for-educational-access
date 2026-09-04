"""Download frozen translation-input release payloads; never upload anything.

Run from any directory with Python 3.12+. Large inputs stay in ignored downloads/.
Metadata/notices are kept verbatim and every selected asset is SHA-256 verified.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
LANG = ROOT / "languages/bn-Beng-IN"
RELEASES = {
    "A00": ("openstax-prealgebra-2e-id-ID", "prealgebra-2e-id-ID-v0.2.7"),
    "A10": ("openstax-elementary-algebra-2e-id", "v1.0.2"),
    "A20": ("openstax-intermediate-algebra-2e-id", "v0.3.0-wip"),
    "A30": ("openstax-precalculus-2e-id", "v0.1.0-alpha.58-reader.1"),
}
# Frozen from anonymous GitHub release metadata on 2026-08-30. No mutable
# /latest lookup is needed for replay (the API may be rate limited).
PAYLOADS = {
    "A00": [
        ("prealgebra-2e-id-ID-v0.2.7-source.zip", "ec622c4b0be5693a798453ee6d1a6ae21cdf978f26852253b5cbb5d88a484fee"),
        ("prealgebra-2e-id-ID-v0.2.7-release-manifest.json", "7f5ca07be141ad06fd1a60d435c9c03aa0258fb106d24cecbb8a8208d8def9ef"),
        ("SHA256SUMS.txt", "6251a8a3cfca0f46d5510365dea078c804db485101c8cba10468a82b9a86dbbb")],
    "A10": [
        ("elementary-algebra-2e-id-ID-1.0.2-source.zip", "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456"),
        ("elementary-algebra-2e-id-ID-1.0.2-release-manifest.json", "55c2e9af12877969729c9224b1264cd644fd21fb8b9d8ec9bdcdac8a0bc59295"),
        ("LICENSE.txt", "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a"),
        ("SHA256SUMS.txt", "5f4abce9a019ea01dd5fb5fa0f4aa61e478cc1699c166fa28dd1596bbe510d8d")],
    "A20": [
        ("openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip", "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
        ("openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-release-manifest.json", "52f4fee5326e8c8138b7ebf6dda54eed431a76d5db0303d7ed973d397ad95294"),
        ("LICENSE.txt", "12f4da8bb2fb5f7a4ae529e03c02e8de48ee8a33c642b75c5ed2f1f9d0323943"),
        ("SHA256SUMS.txt", "08d5088bd222964033c67a99e4e81776ebb10bfef8ee08c924febf479206059f")],
    "A30": [
        ("precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip", "9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca"),
        ("precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-manifest.json", "743d523ba6bf97eb4f958adf719eaabc472fd782161c159aa1b07c5fe61be0ce"),
        ("LICENSE.txt", "b8d4823d420283ad4e9e303f49eebdbf64fbc1d9a2e2fee97030a95ab2a243a3"),
        ("SHA256SUMS.txt", "52d92605798ed0b5143dbbd491a508066ec324a06f9c3f35cb3d4ec7650c649f")]
}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def download(url, dest, expected=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and expected and sha(dest) == expected:
        return
    part = dest.with_name(dest.name + ".part")
    subprocess.run(["curl.exe", "--location", "--fail", "--silent", "--show-error",
                    "--continue-at", "-", "--retry", "5", "--retry-all-errors",
                    "--connect-timeout", "30", "--speed-time", "60", "--speed-limit", "1024",
                    "--output", str(part), url], check=True)
    actual = sha(part)
    if expected and actual != expected:
        raise ValueError(f"Hash mismatch: {dest.name}: {actual} != {expected}")
    part.replace(dest)


def acquire(item):
    course, (repo, tag) = item
    evidence = LANG / "provenance" / course
    assets = []
    for name, expected in PAYLOADS[course]:
        url = f"https://github.com/KokunoYumeto/{repo}/releases/download/{tag}/{name}"
        dest = ROOT / "downloads" / "releases" / course / name if name.endswith(".zip") else evidence / name
        download(url, dest, expected)
        assets.append({"path": dest.relative_to(ROOT).as_posix(), "url": url,
                       "bytes": dest.stat().st_size, "sha256": sha(dest), "expected_sha256": expected})
        print(f"VERIFIED {course}: {name} ({dest.stat().st_size} bytes)", flush=True)
    return {"course": course, "repository": f"https://github.com/KokunoYumeto/{repo}",
            "release_tag": tag, "release_url": f"https://github.com/KokunoYumeto/{repo}/releases/tag/{tag}",
            "digest_authority": "GitHub release asset SHA-256, observed 2026-08-30; also retained release checksums", "assets": assets}


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(acquire, RELEASES.items()))
    out = LANG / "provenance/releases.lock.json"
    out.write_text(json.dumps({"purpose": "translation inputs only; not a training/fine-tuning dataset", "releases": records}, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {out.relative_to(ROOT)}", flush=True)
