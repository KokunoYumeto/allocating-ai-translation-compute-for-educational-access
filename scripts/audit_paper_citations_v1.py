#!/usr/bin/env python3
"""Bounded citation-to-register audit for the active paper draft."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"
REFS = ROOT / "sources" / "REFERENCES_APA.md"
OUT = ROOT / "qa" / "PAPER_CITATION_AUDIT_v1.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    paper = PAPER.read_text(encoding="utf-8")
    refs = REFS.read_text(encoding="utf-8")

    # This intentionally catches the conventional author-year forms used in
    # the draft, while leaving URLs, years in equations, and source IDs alone.
    patterns = [
        r"\b([A-Z][A-Za-z’'\-]+(?:\s+et al\.)?),\s*(\d{4}[a-z]?)\b",
        r"\b([A-Z][A-Za-z’'\-]+\s*&\s*[A-Z][A-Za-z’'\-]+),\s*(\d{4}[a-z]?)\b",
    ]
    citations = sorted({f"{a}, {y}" for pat in patterns for a, y in re.findall(pat, paper)})
    # A citation is considered registered when both the lead author/org and
    # year occur in a bibliography line. This is a triage audit, not a
    # substitute for manual source identity review.
    missing = []
    matched = []
    for citation in citations:
        author, year = citation.rsplit(", ", 1)
        lead = author.replace(" et al.", "").split(" & ")[0].strip()
        if year in refs and lead in refs:
            matched.append(citation)
        else:
            missing.append(citation)

    result = {
        "schema": "interlanguage/paper-citation-audit/1.0.0",
        "paper": {"path": str(PAPER.relative_to(ROOT)), "bytes": PAPER.stat().st_size, "sha256": digest(PAPER)},
        "references": {"path": str(REFS.relative_to(ROOT)), "bytes": REFS.stat().st_size, "sha256": digest(REFS)},
        "citation_count": len(citations),
        "matched_count": len(matched),
        "missing_or_unresolved_count": len(missing),
        "citations": citations,
        "matched": matched,
        "missing_or_unresolved": missing,
        "interpretation": "This bounded string audit identifies citations requiring bibliography review; a match does not prove that the cited source supports the claim.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUT), "bytes": OUT.stat().st_size, "sha256": digest(OUT), "missing": missing}, sort_keys=True))


if __name__ == "__main__":
    main()
