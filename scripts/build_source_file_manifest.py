from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "sources"
OUTPUT = ROOT / "SOURCE_FILE_MANIFEST.csv"


SOURCE_URLS = {
    "UIS_SDG_202602.zip": "https://download.uis.unesco.org/bdds/202602/SDG.zip",
    "UIS_DEM_202602.zip": "https://download.uis.unesco.org/bdds/202602/DEM.zip",
    "UIS_SCN_SDG_202602.zip": "https://download.uis.unesco.org/bdds/202602/SCN-SDG.zip",
    "WORLD_BANK_LEARNING_POVERTY_2024.xls": "https://datacatalog.worldbank.org/search/dataset/0038947/learning-poverty-global-database-historical-data-and-sub-components",
    "WORLD_BANK_LEARNING_POVERTY_2024.xlsx": "derived locally from WORLD_BANK_LEARNING_POVERTY_2024.xls by LibreOffice conversion; source bytes preserved",
    "ITU_GLOBAL_REGIONAL_ICT_2025.xlsx": "https://www.itu.int/itu-d/reports/statistics/facts-figures-2025/",
    "uis_202602/SDG_DATA_NATIONAL.csv": "https://download.uis.unesco.org/bdds/202602/SDG.zip",
    "uis_202602/SDG_LABEL.csv": "https://download.uis.unesco.org/bdds/202602/SDG.zip",
    "uis_202602/SDG_COUNTRY.csv": "https://download.uis.unesco.org/bdds/202602/SDG.zip",
    "uis_202602/SDG_README_RELEASE_2026_February.md": "https://download.uis.unesco.org/bdds/202602/SDG.zip",
    "uis_202602/DEM_DATA_NATIONAL.csv": "https://download.uis.unesco.org/bdds/202602/DEM.zip",
    "uis_202602/DEM_LABEL.csv": "https://download.uis.unesco.org/bdds/202602/DEM.zip",
    "uis_202602/DEM_COUNTRY.csv": "https://download.uis.unesco.org/bdds/202602/DEM.zip",
    "uis_202602/DEM_README_RELEASE_2026_February.md": "https://download.uis.unesco.org/bdds/202602/DEM.zip",
    "uis_202602/SCN-SDG_DATA_NATIONAL.csv": "https://download.uis.unesco.org/bdds/202602/SCN-SDG.zip",
    "uis_202602/SCN-SDG_LABEL.csv": "https://download.uis.unesco.org/bdds/202602/SCN-SDG.zip",
    "uis_202602/SCN-SDG_COUNTRY.csv": "https://download.uis.unesco.org/bdds/202602/SCN-SDG.zip",
    "uis_202602/SCN-SDG_README_RELEASE_2026_February.md": "https://download.uis.unesco.org/bdds/202602/SCN-SDG.zip",
    "web_snapshots/OPENSTAX_BOOK_CATALOG_20260901.json": "https://openstax.org/apps/cms/api/v2/pages/30/",
    "web_snapshots/OPEN_LOGIC_ABOUT_20260901.html": "https://openlogicproject.org/about/",
    "web_snapshots/OPEN_LOGIC_BUILDS_20260901.html": "https://builds.openlogicproject.org/",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def source_url(relative: str) -> str:
    normalized = relative.replace("\\", "/")
    if normalized.startswith("world_bank_api/"):
        indicator = Path(normalized).stem
        return (
            "https://api.worldbank.org/v2/country/all/indicator/"
            f"{indicator}?format=json&per_page=20000"
        )
    return SOURCE_URLS.get(normalized, "")


def main() -> None:
    rows = []
    for path in sorted(SOURCE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(SOURCE_ROOT).as_posix()
        rows.append(
            {
                "source_file_id": f"FILE-{len(rows) + 1:03d}",
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "source_url_or_derivation": source_url(relative),
                "role": "downloaded_source" if "derived locally" not in source_url(relative) else "format_conversion",
            }
        )

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
