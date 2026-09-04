"""Acquire translation inputs only; release metadata and digest checks are receipts.

Large ZIPs and expanded texts stay in ignored downloads/. No dataset is created.
"""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DOWNLOADS = ROOT / "downloads" / "gu-Gujr-IN"
RECEIPTS = ROOT / "gu-Gujr-IN" / "provenance"
RELEASES = {
    "a00": ("openstax-prealgebra-2e-id-ID", "prealgebra-2e-id-ID-v0.2.7"),
    "a10": ("openstax-elementary-algebra-2e-id", "v1.0.2"),
}
# Transcribed selected asset digests from GitHub's releases/latest API on
# 2026-08-30. Pinned here so acquisition does not require API quota.
PINNED_ASSETS = {
    "a00": {
        "prealgebra-2e-id-ID-v0.2.7-source.zip": "ec622c4b0be5693a798453ee6d1a6ae21cdf978f26852253b5cbb5d88a484fee",
        "prealgebra-2e-id-ID-v0.2.7-release-manifest.json": "7f5ca07be141ad06fd1a60d435c9c03aa0258fb106d24cecbb8a8208d8def9ef",
        "SHA256SUMS.txt": "6251a8a3cfca0f46d5510365dea078c804db485101c8cba10468a82b9a86dbbb",
    },
    "a10": {
        "elementary-algebra-2e-id-ID-1.0.2-source.zip": "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456",
        "elementary-algebra-2e-id-ID-1.0.2-release-manifest.json": "55c2e9af12877969729c9224b1264cd644fd21fb8b9d8ec9bdcdac8a0bc59295",
        "LICENSE.txt": "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a",
        "SHA256SUMS.txt": "5f4abce9a019ea01dd5fb5fa0f4aa61e478cc1699c166fa28dd1596bbe510d8d",
    },
}


def download(url, destination):
    req = urllib.request.Request(url, headers={"User-Agent": "Gujarati-translation-acquisition"})
    with urllib.request.urlopen(req, timeout=120) as response, destination.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)


def acquire(key, repo, tag):
    folder = DOWNLOADS / (key + "-release")
    folder.mkdir(parents=True, exist_ok=True)
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    acquired = []
    for name, expected in PINNED_ASSETS[key].items():
        url = f"https://github.com/KokunoYumeto/{repo}/releases/download/{tag}/{name}"
        path = folder / name
        if not path.exists() or hashlib.file_digest(path.open("rb"), "sha256").hexdigest() != expected:
            download(url, path)
        actual = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Digest mismatch: {path}")
        acquired.append({"file": path.relative_to(ROOT).as_posix(), "url": url,
                         "bytes": path.stat().st_size, "sha256": actual, "github_digest_verified": True})
        if path.suffix == ".zip":
            expanded = folder / "source"
            with zipfile.ZipFile(path) as archive:
                base = expanded.resolve()
                for member in archive.infolist():
                    target = (expanded / member.filename).resolve()
                    if not target.is_relative_to(base):
                        raise ValueError("Archive path escapes destination")
                archive.extractall(expanded)
        else:
            (RECEIPTS / (key + "-" + name)).write_bytes(path.read_bytes())
        print(f"Verified {key}: {name} ({path.stat().st_size:,} bytes)", flush=True)
    (RECEIPTS / (key + "-assets.json")).write_text(json.dumps(acquired, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda row: acquire(row[0], *row[1]), RELEASES.items()))
