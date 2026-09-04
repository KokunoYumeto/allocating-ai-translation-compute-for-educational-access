from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "sources" / "web_snapshots" / "OPENSTAX_BOOK_CATALOG_20260901.json"
BOOK_OUTPUT = ROOT / "OPENSTAX_CATALOG_20260901.csv"
SUBJECT_OUTPUT = ROOT / "OPENSTAX_SUBJECT_COUNTS_20260901.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def joined(values: object) -> str:
    if not isinstance(values, list):
        return ""
    return "; ".join(str(value) for value in values)


def main() -> None:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    rows = []
    subject_counts: Counter[str] = Counter()
    for book in data.get("books", []):
        if book.get("book_state") != "live":
            continue
        subjects = book.get("subjects") or []
        for subject in subjects:
            subject_counts[str(subject)] += 1
        rows.append(
            {
                "openstax_book_id": book.get("id", ""),
                "title": book.get("title", ""),
                "slug": book.get("slug", ""),
                "subjects": joined(subjects),
                "subject_categories": joined(book.get("subject_categories")),
                "k12_subjects": joined(book.get("k12subject")),
                "is_ap": str(bool(book.get("is_ap"))).lower(),
                "is_high_school": str(bool(book.get("is_hs"))).lower(),
                "pdf_url": book.get("pdf_url", ""),
                "web_url": book.get("webview_rex_link", "") or book.get("webview_link", ""),
                "bookshare_url": book.get("bookshare_link", ""),
                "audiobook_url": book.get("audiobook_link", ""),
                "faculty_resources": str(bool(book.get("has_faculty_resources"))).lower(),
                "student_resources": str(bool(book.get("has_student_resources"))).lower(),
                "snapshot_sha256": sha256(SNAPSHOT),
            }
        )

    fields = list(rows[0].keys())
    with BOOK_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["title"].casefold()))

    with SUBJECT_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["subject", "live_title_count"])
        writer.writeheader()
        for subject, count in sorted(subject_counts.items()):
            writer.writerow({"subject": subject, "live_title_count": count})

    print(
        json.dumps(
            {
                "live_titles": len(rows),
                "subjects": dict(sorted(subject_counts.items())),
                "snapshot_sha256": sha256(SNAPSHOT),
                "catalog_sha256": sha256(BOOK_OUTPUT),
                "subject_counts_sha256": sha256(SUBJECT_OUTPUT),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
